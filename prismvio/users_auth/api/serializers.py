import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.utils import timezone
from firebase_admin import auth
from firebase_admin.auth import ExpiredIdTokenError
from loguru import logger
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import PasswordField, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from prismvio.core.firebase import get_firebase_admin_service
from prismvio.location.models import Country, District, Province, Ward
from prismvio.menu_merchant.models import Category
from prismvio.merchant.models import Merchant
from prismvio.users.api.validate_serializers import UserValidationSerializer, VerificationIdSerializer
from prismvio.users.enums import OTPAction
from prismvio.users_auth.exceptions import LoginFailException
from prismvio.utils.exceptions import CODE

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
            raise LoginFailException()


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

        otp_obj = self.check_verification_id(signature, email, otp, OTPAction.PASSWORD_RESET.value)
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


class ValidateEmailVerificationCodeSerializer(serializers.Serializer):
    verification_id = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    email = serializers.EmailField(max_length=255, required=True)
