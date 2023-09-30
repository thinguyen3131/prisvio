import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import exceptions, serializers

from prismvio.core.configs import CURRENCY
from prismvio.location.models import Country, District, Province, Ward
from prismvio.menu_merchant.models import Category
from prismvio.users.api.validate_serializers import UserValidationSerializer
from prismvio.users.models.user import PrivacySetting

User = get_user_model()


def raise_throttled(wait=None, detail=None):
    exc = exceptions.Throttled(wait=wait, detail=detail)
    exc.code = "otp_request_limited"
    raise exc


def validate_password(password):
    """
    Validates the password to ensure it has at least one uppercase letter, one lowercase letter,
    one digit, one special character (@, #, $, %, ...) and is at least 8 characters long.
    """
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r"[@#$%^&+=]", password):
        raise serializers.ValidationError(
            "Password must contain at least one special character such as @, #, $, %, ..."
        )
    return password


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


class SendEmailVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)


class ValidateEmailVerificationCodeSerializer(serializers.Serializer):
    verification_id = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    email = serializers.EmailField(max_length=255, required=True)


class EmailPhoneLookupSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.CharField(), required=False)
    phones = serializers.ListField(child=serializers.CharField(), required=False)
    link = serializers.CharField(required=False)

    def to_internal_value(self, data):
        for f in ["emails", "phones"]:
            if data.get(f):
                # Get unique elements, preserving order
                data[f] = list(dict.fromkeys(data[f]))
        return super().to_internal_value(data)

    def validate(self, data):
        if not data.get("emails") and not data.get("phones"):
            raise serializers.ValidationError('Fields "emails" or "phones" required.')
        return data


class MeDetailSerializer(UserValidationSerializer):
    """Serializer specifically for viewing and editing current user's profile"""

    currency = serializers.CharField(required=False)
    verification_id = serializers.CharField(required=False, write_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_null=True, write_only=True
    )
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
            "email",
            "phone_number",
            "birth_date",
            "first_name",
            "middle_name",
            "last_name",
            "brand_name",
            "full_name",
            "bio",
            "birth_date",
            "website",
            "language",
            "gender",
            "is_share_phone",
            "currency",
            "categories",
            "category_ids",
            "address",
            "latitude",
            "longitude",
            "country_code",
            "verified_email_at",
            "verified_phone_number_at",
            "email_verified",
            "phone_verified",
            "is_registered",
            "avatar",
            "banner",
            "verification_id",
            "id_token",
            "is_active",
            "country_id",
            "province_id",
            "district_id",
            "ward_id",
            "country",
            "province",
            "district",
            "ward",
        )
        read_only_fields = ("verified_email_at", "verified_phone_number_at")

    def validate(self, attrs):
        return self.validate_identity_info(attrs)

    def update(self, instance, validated_data):
        email = validated_data.get("email", None)
        signature = validated_data.pop("verification_id", None)
        phone_number = validated_data.get("phone_number", None)
        id_token = validated_data.pop("id_token", None)
        email_verified = validated_data.get("email_verified", None)
        phone_verified = validated_data.get("phone_verified", None)
        category_ids = validated_data.pop("category_ids", None)
        otp_obj = None
        if email and instance.email != email and email_verified is True:
            otp_obj = self.check_verification_id(signature, email)
            validated_data["verified_email_at"] = timezone.now()

        if phone_number and instance.phone_number != phone_number and phone_verified is True:
            self.check_id_token(id_token, phone_number)
            validated_data["verified_phone_number_at"] = timezone.now()

        if category_ids is not None:
            instance.categories.set(category_ids)

        for k, v in validated_data.items():
            if k == "title":
                v = instance.get_or_create_user_title(v)
            if k == "currency":
                if any(v in cur for cur in CURRENCY):
                    """Convert wallet balance by new currency setting"""
                    if v != instance.currency:
                        instance.convert_wallet_balance_by_exchange_rate(
                            curr_from=instance.currency,
                            curr_to=v,
                        )
                else:
                    continue
            setattr(instance, k, v)
        instance.save()
        if otp_obj:
            otp_obj.is_used = True
            otp_obj.save()
        return instance


class UpdatePasswordSerializer(serializers.Serializer):
    """Serializer for regular case of password update"""

    password = serializers.CharField(max_length=256, required=True)
    new_password = serializers.CharField(max_length=256, required=True)

    def validate_password(self, raw_password):
        """Validate new password and check current"""
        user = self.context["request"].user
        if not user.check_password(raw_password):
            raise serializers.ValidationError(_("Invalid password"))
        return raw_password

    def validate_new_password(self, raw_password):
        try:
            django_validate_password(raw_password)
        except Exception:
            raise serializers.ValidationError(_("Invalid new password"))
        return raw_password


class DeactivateUserActiveStatusSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)


class PrivacySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacySetting
        fields = "__all__"


class SubUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=100)
    parent_id = serializers.IntegerField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "full_name", "phone_number", "password", "gender", "parent_id"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
            raise serializers.ValidationError(_("username has already exists"))
        except User.DoesNotExist:
            return value

    def validate_password(self, value):
        try:
            django_validate_password(value)
        except Exception:
            raise serializers.ValidationError(_("Invalid password"))
        return value

    def validate_parent_id(self, value):
        try:
            parent = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Parent user with the given id does not exist"))
        return parent

    def create(self, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")
        parent = validated_data.get("parent_id")
        data = {
            "username": username,
            "password": make_password(password),
            "full_name": username,
            "gender": parent.gender,
            "parent_id": parent.pk,
        }
        return super().create(data)
