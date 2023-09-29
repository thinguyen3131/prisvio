from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase

from prismvio.users.enums import OTPType
from prismvio.users.otp import LimitedError, get_otp_instance, is_valid_otp_instance
from prismvio.users_auth.api.serializers import (
    EmailPasswordResetSerializer,
    LoginSerializer,
    PhonePasswordResetSerializer,
    PrismTokenRefreshSerializer,
    UserCreateSerializer,
    ValidateEmailVerificationCodeSerializer,
)
from prismvio.users_auth.exceptions import ExpiredOTPException, InvalidOTPException, OTPRequestLimitedException


class LoginAPIView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    It's similar to TokenObtainPairView from rest_framework_simplejwt package
    but uses custom serializer class
    """

    serializer_class = LoginSerializer


class PrismTokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = PrismTokenRefreshSerializer


class SignupAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {"id": user.id, "user": serializer.data, "refresh": str(refresh), "access": str(refresh.access_token)},
                status=status.HTTP_201_CREATED,
            )
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhonePasswordResetView(CreateAPIView):
    serializer_class = PhonePasswordResetSerializer
    permission_classes = ()


class EmailPasswordResetView(CreateAPIView):
    serializer_class = EmailPasswordResetSerializer
    permission_classes = ()


class ValidateEmailVerificationCode(APIView):
    serializer = ValidateEmailVerificationCodeSerializer
    permission_classes = ()

    def post(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        code = serializer.data.get("code")
        signature = serializer.data.get("verification_id")

        instance = get_otp_instance(
            signature=signature,
            otp_type=OTPType.EMAIL.value,
        )
        if not instance or instance.email != email:
            raise ExpiredOTPException()
        try:
            interval = int(settings.EMAIL_VERIFICATION_CODE_TIMEOUT)
            if not is_valid_otp_instance(instance, code, interval):
                raise InvalidOTPException
        except LimitedError:
            raise OTPRequestLimitedException()

        if not instance.is_verified:
            instance.is_verified = True
            instance.save()

        return Response(
            {
                "message": "valid",
                "verification_id": signature,
            },
            status=status.HTTP_200_OK,
        )
