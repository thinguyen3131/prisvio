import jwt
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import PasswordField, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from prismvio.users_auth.exceptions import LoginFailException

User = get_user_model()


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