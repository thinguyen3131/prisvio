from datetime import timedelta

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from firebase_admin import auth
from firebase_admin.auth import ExpiredIdTokenError
from loguru import logger
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import PasswordField, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from prismvio.location.models import Country, District, Province, Ward
from prismvio.menu_merchant.models import Category
from prismvio.merchant.models import Merchant
from prismvio.users.enums import IntervalLockTime, OTPAction, OTPType
from prismvio.users.models.otp import OneTimePassword
from prismvio.users.otp import LimitedError, get_otp_instance, is_valid_otp_instance
from prismvio.users_auth.exceptions import LoginFailException
from prismvio.utils.exceptions import CODE
from prismvio.utils.firebase import get_firebase_admin_service
from prismvio.utils.phonenumber import get_country_code_from_phone_number, validate_phone_number

User = get_user_model()


def raise_throttled(wait=None, detail=None):
    exc = exceptions.Throttled(wait=wait, detail=detail)
    exc.code = "otp_request_limited"
    raise exc


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "full_name_vi", "full_name_en")


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name_vi", "name_en")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "middle_name", "last_name", "full_name")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = PasswordField()

    def validate(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        username = attrs.get("username")
        password = attrs.get("password")
        user = None
        try:
            if email:
                user = User.objects.get(email=email)
            elif phone_number:
                user = User.objects.get(phone_number=phone_number)
            elif username:
                user = User.objects.get(username=username)
            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            else:
                raise LoginFailException()
        except User.DoesNotExist:
            raise ()


class PrismTokenRefreshSerializer(TokenRefreshSerializer):
    """Add check subscription function by token"""

    def validate(self, attrs):
        data = super().validate(attrs)
        payload = jwt.decode(data["access"], options={"verify_signature": False})
        user = User.objects.get(pk=payload["user_id"])
        if not user.is_active:
            raise LoginFailException
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


# Editable user serializers #


class VerificationIdSerializer(serializers.Serializer):
    verification_id = serializers.CharField(required=False, write_only=True, allow_blank=True, allow_null=True)
    otp = serializers.CharField(write_only=True, required=False)

    def check_verification_id(self, signature, email, otp):
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
            otp_action=OTPAction.ID_VERIFICATION.value,
            is_verified=False,
            last_send__gte=past_time,
            is_used=False,
        ).last()
        if not otp_obj:
            raise exceptions.ValidationError(
                "The verification ID is not valid 222",
                "invalid_verification_id",
            )

        instance = get_otp_instance(
            signature=signature,
            otp_type=OTPType.EMAIL.value,
        )
        if not instance or instance.email != email:
            raise exceptions.NotFound("Expired OTP", "OTP_NOT_FOUND")
        try:
            interval = int(settings.EMAIL_VERIFICATION_CODE_TIMEOUT)
            if not is_valid_otp_instance(instance, otp, interval):
                raise exceptions.ParseError("Invalid OTP.", "otp_invalid")
        except LimitedError:
            raise_throttled(IntervalLockTime.CHECK)
        if otp_obj:
            otp_obj.is_used = True
            otp_obj.is_verified = True
            otp_obj.save()
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
        phone_verified = int(attrs.get("phone_verified", 0))
        email_verified = int(attrs.get("email_verified", 0))
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

        if not email and not phone_number:
            raise serializers.ValidationError(
                {
                    CODE.USER.MISSING_EMAIL_OR_PHONE: _("You must enter at least one of email or phone number."),
                }
            )

        if not email_verified and not phone_verified:
            raise serializers.ValidationError(
                {
                    CODE.USER.MISSING_FIELD_VERIFIED: _(
                        "You must enter at least one of email verified or phone number verified"
                    ),
                }
            )
        attrs["phone_verified"] = True if phone_verified else False
        attrs["email_verified"] = True if email_verified else False

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


class UserCreateSerializer(UserValidationSerializer):
    """Serializer specifically for user creation"""

    category_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

    country = CountrySerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    ward = WardSerializer(read_only=True)

    country_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="country", required=False, queryset=Country.objects.all()
    )
    province_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="province", required=False, queryset=Province.objects.all()
    )
    district_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="district", required=False, queryset=District.objects.all()
    )
    ward_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="ward", required=False, queryset=Ward.objects.all()
    )

    class Meta:
        model = User
        fields = (
            "id",
            "profile_type",
            "birth_date",
            "email",
            "phone_number",
            "country_code",
            "password",
            "country_id",
            "country",
            "province",
            "district",
            "ward",
            "province_id",
            "district_id",
            "ward_id",
            "first_name",
            "middle_name",
            "last_name",
            "brand_name",
            "full_name",
            "email_verified",
            "phone_verified",
            "category_ids",
            "verification_id",
            "otp",
            "id_token",
            "verified_email_at",
            "verified_phone_number_at",
            "username",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }
        read_only_fields = ("verified_email_at", "verified_phone_number_at")

    def validate_password(self, raw_password):
        django_validate_password(raw_password)
        return raw_password

    def validate(self, attrs):
        return self.validate_identity_info(attrs)

    def create(self, validated_data):
        email = validated_data.get("email", None)
        signature = validated_data.pop("verification_id", None)
        phone_number = validated_data.get("phone_number", None)
        id_token = validated_data.pop("id_token", None)
        email_verified = validated_data.get("email_verified")
        phone_verified = validated_data.get("phone_verified")
        category_ids = validated_data.pop("category_ids", [])
        otp = validated_data.pop("otp", None)

        otp_obj = None
        if email and email_verified:
            otp_obj = self.check_verification_id(signature, email, otp)
            validated_data["verified_email_at"] = timezone.now()

        if phone_number and phone_verified:
            self.check_id_token(id_token, phone_number)
            validated_data["verified_phone_number_at"] = timezone.now()

        validated_data["password"] = make_password(validated_data["password"])
        user = self.Meta.model(**validated_data)
        user.first_time_login = True
        user.save()
        if otp_obj:
            otp_obj.is_used = True
            otp_obj.save()
        # Create merchant when register business profile
        if user.profile_type == User.BUSINESS_PROFILE:
            merchant = Merchant.objects.create(
                owner=user,
                email=user.email,
                phone_number=user.phone_number,
                name=user.brand_name,
                country_code=user.country_code,
            )
            merchant.categories.set(category_ids)

        return user


class PhonePasswordResetSerializer(serializers.ModelSerializer):
    id_token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "id_token",
            "password",
        )

    def validate_password(self, raw_password):
        django_validate_password(raw_password)
        return raw_password

    def create(self, validated_data):
        password = validated_data.get("password")
        id_token = validated_data.get("id_token")
        _ = get_firebase_admin_service()

        try:
            decoded_token = auth.verify_id_token(id_token)
        except ExpiredIdTokenError:
            raise exceptions.ValidationError("Expired ID Token.", CODE.USER.EXPIRED_ID_TOKEN)
        except Exception as err:
            logger.error(str(err))
            raise exceptions.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        if not decoded_token or not isinstance(decoded_token, dict):
            raise exceptions.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        if "phone_number" not in decoded_token or not decoded_token["phone_number"]:
            raise exceptions.ValidationError("Invalid ID Token.", CODE.USER.INVALID_ID_TOKEN)

        phone_number = decoded_token["phone_number"]
        try:
            user = User.objects.get(
                phone_number=phone_number,
            )
            raw_password = password
            user.set_password(raw_password)
            user.verified_phone_number_at = timezone.now()
            user.save()
            return user
        except User.DoesNotExist:
            raise exceptions.NotFound("User not found", "user_not_found")

    def to_representation(self, instance):
        return {
            "success": True,
            "phone_number": instance.phone_number,
        }


class EmailPasswordResetSerializer(serializers.ModelSerializer, VerificationIdSerializer):
    email = serializers.EmailField(required=True)
    verification_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    otp = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "verification_id",
            "otp",
        )

    def validate_password(self, raw_password):
        django_validate_password(raw_password)
        return raw_password

    def create(self, validated_data):
        signature = validated_data.get("verification_id")
        email = validated_data.get("email")
        otp = validated_data.get("otp")
        password = validated_data.get("password")

        otp_obj = self.check_verification_id(signature, email, otp)
        try:
            user = User.objects.get(
                email=email,
            )
        except User.DoesNotExist:
            raise exceptions.NotFound("User not found", "user_not_found")

        user.set_password(password)
        user.verified_email_at = timezone.now()
        user.save()

        otp_obj.is_used = True
        otp_obj.save()
        return user

    def to_representation(self, instance):
        return {
            "success": True,
            "phone_number": instance.email,
        }
