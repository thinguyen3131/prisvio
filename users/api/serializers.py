from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model
from ..models.user import User
from ..models.otp import OneTimePassword
from django.utils import timezone
from datetime import datetime, timedelta
from users.enums import IntervalLockTime, OTPType, OTPAction
import pyotp
import re
from django.conf import settings
from users.otp import LimitedError, get_otp_instance, is_valid_otp_instance, require_new_otp
from django.contrib.auth.password_validation import validate_password as django_validate_password

User = get_user_model()


def raise_throttled(wait=None, detail=None):
    exc = exceptions.Throttled(wait=wait, detail=detail)
    exc.code = 'otp_request_limited'
    raise exc

def validate_password(password):
    """
    Validates the password to ensure it has at least one uppercase letter, one lowercase letter,
    one digit, one special character (@, #, $, %, ...) and is at least 8 characters long.
    """
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'[0-9]', password):
        raise serializers.ValidationError("Password must contain at least one digit.")
    if not re.search(r'[@#$%^&+=]', password):
        raise serializers.ValidationError("Password must contain at least one special character such as @, #, $, %, ...")
    return password


class UserSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(write_only=True, required=True)
    verification_id = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'role', 'gender', 'marital_status', 'parent_id', 'otp', 'verification_id']
        extra_kwargs = {'password': {'write_only': True}}

    # def validate_password(self, value):
    #     return validate_password(value)

    def check_verification_id(self, signature, email, otp):
        if not signature:
            raise exceptions.ValidationError(
                'The verification ID is not valid 111111',
                'invalid_verification_id',
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
                'The verification ID is not valid 222',
                'invalid_verification_id',
            )
        
        instance = get_otp_instance(
            signature=signature,
            otp_type=OTPType.EMAIL.value,
        )
        if not instance or instance.email != email:
            raise exceptions.NotFound('Expired OTP', "OTP_NOT_FOUND")
        try:
            interval = int(settings.EMAIL_VERIFICATION_CODE_TIMEOUT)
            if not is_valid_otp_instance(instance, otp, interval):
                raise exceptions.ParseError('Invalid OTP.', 'otp_invalid')
        except LimitedError:
            raise_throttled(IntervalLockTime.CHECK)
        if otp_obj:
            otp_obj.is_used = True
            otp_obj.is_verified= True
            otp_obj.save()
        return otp_obj

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        email = validated_data.get('email', None)
        signature = validated_data.pop('verification_id', None)
        otp = validated_data.pop('otp', None)
        phone_number = validated_data.get('phone_number', None)
        

        otp_obj = None
        if email:
            otp_obj = self.check_verification_id(signature, email, otp)
            validated_data['verified_email_at'] = timezone.now()

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if otp_obj:
            otp_obj.user_id = user.id
            otp_obj.save()
        return user

class UserCloneSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'role', 'gender', 'marital_status', 'parent_id', 'business_admin']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        password = validated_data.get('password')
        # Create a new user with the provided data
        user = User.objects.create(**validated_data)

        # Set the parent_id if provided
        if parent_id:
            user.parent_id = parent_id.id

        # Set the password for the user
        user.set_password(password)
        user.save()

        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class SendEmailVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)


class ValidateEmailVerificationCodeSerializer(serializers.Serializer):
    verification_id = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    email = serializers.EmailField(max_length=255, required=True)


class EmailPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_id = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, raw_password):
        django_validate_password(raw_password)
        return raw_password