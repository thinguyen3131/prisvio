from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from firebase_admin import auth
from firebase_admin.auth import ExpiredIdTokenError
from loguru import logger
from rest_framework import exceptions, serializers

from prismvio.core.firebase import get_firebase_admin_service
from prismvio.users.enums import IntervalLockTime, OTPAction, OTPType
from prismvio.users.models.otp import OneTimePassword
from prismvio.utils.exceptions import CODE
from prismvio.utils.phonenumber import get_country_code_from_phone_number, validate_phone_number

User = get_user_model()


def raise_throttled(wait=None, detail=None):
    exc = exceptions.Throttled(wait=wait, detail=detail)
    exc.code = "otp_request_limited"
    raise exc


class VerificationIdSerializer(serializers.Serializer):
    verification_id = serializers.CharField(required=False, write_only=True, allow_blank=True, allow_null=True)

    def check_verification_id(self, signature, email, otp_action=OTPAction.ID_VERIFICATION.value):
        if not signature:
            raise exceptions.ValidationError(
                "The verification ID is not valid 111111",
                "invalid_verification_id",
            )

        now = timezone.now()
        past_time = now - timedelta(minutes=IntervalLockTime.SEND.value)
        otp_obj = OneTimePassword.objects.filter(
            signature=signature,
            otp_type=OTPType.EMAIL.value,
            email=email,
            otp_action=otp_action,
            is_verified=True,
            last_send__gte=past_time,
            is_used=False,
        ).last()
        if not otp_obj:
            raise exceptions.ValidationError(
                "The verification ID is not valid.",
                "invalid_verification_id",
            )
        return otp_obj


class PhoneNumberValidationMixin:
    def validate_phone_number(self, phone_number):
        if not phone_number:
            return phone_number

        phone_number_from_input = None
        try:
            phone_number_from_input = validate_phone_number(phone_number)
        except exceptions.ValidationError:
            pass

        if not phone_number_from_input:
            try:
                phone_number_from_input = validate_phone_number(
                    phone_number,
                    country_code=settings.DEFAULT_COUNTRY_CODE,
                )
            except exceptions.ValidationError:
                raise exceptions.ValidationError("The phone number is not valid.", "phone_number")

        return phone_number_from_input


class IdTokenSerializer(PhoneNumberValidationMixin, serializers.Serializer):
    id_token = serializers.CharField(required=False, write_only=True, allow_blank=True, allow_null=True)

    def check_phone_number(self, decoded_token, phone_number):
        if "phone_number" not in decoded_token or not decoded_token["phone_number"]:
            raise exceptions.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        decoded_phone_number = decoded_token["phone_number"]
        if decoded_phone_number == phone_number:
            return True

        try:
            phone_number_from_token = validate_phone_number(
                decoded_phone_number,
            )
        except exceptions.ValidationError:
            phone_number_from_token = validate_phone_number(
                decoded_phone_number,
                country_code=settings.DEFAULT_COUNTRY_CODE,
            )

        try:
            phone_number_from_input = validate_phone_number(
                phone_number,
            )
        except exceptions.ValidationError:
            phone_number_from_input = validate_phone_number(
                phone_number,
                country_code=settings.DEFAULT_COUNTRY_CODE,
            )

        if phone_number_from_token != phone_number_from_input:
            logger.info(f"Invalid phone number from ID token {decoded_phone_number} - {phone_number}")
            raise exceptions.ValidationError("Invalid phone number in the ID token.", "invalid_phone_number")

    def check_id_token(self, id_token, phone_number):
        _ = get_firebase_admin_service()
        if not id_token:
            raise serializers.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        try:
            decoded_token = auth.verify_id_token(id_token)
        except ExpiredIdTokenError:
            raise exceptions.ValidationError("Expired ID Token.", CODE.USER.EXPIRED_ID_TOKEN)
        except Exception as err:
            logger.error(str(err))
            raise serializers.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        if not decoded_token or not isinstance(decoded_token, dict):
            raise exceptions.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        self.check_phone_number(decoded_token, phone_number)


class UserValidationSerializer(
    VerificationIdSerializer,
    IdTokenSerializer,
    serializers.ModelSerializer,
):
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)
    profile_type = serializers.ChoiceField(choices=User.PROFILE_TYPE_CHOICES, required=True)
    country_code = serializers.CharField(required=False)
    username = serializers.CharField(required=False, allow_null=True)
    email_verified = serializers.CharField(required=False, allow_null=True)
    phone_verified = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email",
            "phone_number",
            "country_code",
            "profile_type",
            "username",
        )

    default_error_messages = {
        "not_applicable_for_type": "This field is not applicable for this account type.",
        "required_for_type": "This field is required for this account type.",
    }

    def validate_identity_info(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        username = attrs.get("username")
        profile_type = attrs.get("profile_type")
        # TODO update logic
        phone_verified = None
        email_verified = None
        if "phone_verified" in attrs:
            phone_verified = int(attrs.pop("phone_verified", 0))
            attrs["phone_verified"] = True if phone_verified else False
        if "email_verified" in attrs:
            email_verified = int(attrs.pop("email_verified", 0))
            attrs["email_verified"] = True if email_verified else False
        queryset = User.objects.filter()

        if self.instance:
            assert self.instance.id
            queryset = queryset.exclude(id=self.instance.id)
            if not email:
                email = getattr(self.instance, "email", None)
            if not phone_number:
                phone_number = getattr(self.instance, "phone_number", None)
            if not profile_type:
                profile_type = getattr(self.instance, "profile_type", None)
            if not username:
                username = getattr(self.instance, "username", None)

        if email is not None:
            if queryset.filter(email=email).exists():
                raise serializers.ValidationError(
                    {
                        "email": "The email is not valid.",
                    }
                )
        if phone_number is not None:
            existed = queryset.filter(phone_number=phone_number).exists()
            if existed:
                raise serializers.ValidationError(
                    {
                        "phone_number": "The phone number is not valid.",
                    }
                )

        if username is not None:
            existed = queryset.filter(username=username).exists()
            if existed:
                raise serializers.ValidationError(
                    {
                        "username": "The username is not valid.",
                    }
                )

        if not email and not phone_number and not username:
            raise serializers.ValidationError(
                {
                    CODE.USER.MISSING_EMAIL_OR_PHONE: _(
                        "You must enter at least one of email or phone number or username."
                    ),
                }
            )
        if email_verified == 0 and phone_verified == 0:
            raise serializers.ValidationError(
                {
                    CODE.USER.MISSING_FIELD_VERIFIED: _(
                        "You must enter at least one of email verified or phone number verified"
                    ),
                }
            )

        if phone_number:
            country_code = get_country_code_from_phone_number(phone_number)
            attrs.update(
                {
                    "country_code": country_code,
                }
            )

        profile_type_fields = User.PROFILE_FIELDS_MAP[profile_type]
        errors = {}
        for field in profile_type_fields["not_applicable"]:
            if field in attrs:
                errors[field] = self.error_messages["not_applicable_for_type"]
        for field in profile_type_fields["required"]:
            if not attrs.get(field) and not getattr(self.instance, field, None):
                errors[field] = self.error_messages["required_for_type"]
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
