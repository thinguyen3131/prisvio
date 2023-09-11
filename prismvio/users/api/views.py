from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from prismvio.users.api.serializers import SendEmailVerificationCodeSerializer, ValidateEmailVerificationCodeSerializer
from prismvio.users.enums import IntervalLockTime, OTPAction, OTPType
from prismvio.users.models.otp import OneTimePassword
from prismvio.users.otp import LimitedError, get_otp_instance, is_valid_otp_instance, require_new_otp
from prismvio.users.tasks import send_email_verification_otp_by_email_template

User = get_user_model()


# class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     lookup_field = "pk"

#     def get_queryset(self, *args, **kwargs):
#         assert isinstance(self.request.user.id, int)
#         return self.queryset.filter(id=self.request.user.id)

#     @action(detail=False)
#     def me(self, request):
#         serializer = UserSerializer(request.user, context={"request": request})
#         return Response(status=status.HTTP_200_OK, data=serializer.data)


def raise_throttled(wait=None, detail=None):
    exc = exceptions.Throttled(wait=wait, detail=detail)
    exc.code = "OTP_REQUEST_LIMITED"
    raise exc


class EmailVerificationCodeBaseView(APIView):
    serializer = SendEmailVerificationCodeSerializer
    permission_classes = ()

    def get_otp_action(self):
        return OTPAction.ID_VERIFICATION.value

    def validate_email(self, email):
        pass

    def post(self, request):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        self.validate_email(email)
        otp_action = self.get_otp_action()

        interval = int(settings.EMAIL_VERIFICATION_CODE_TIMEOUT)

        now = timezone.now()
        past_time = now - timedelta(minutes=IntervalLockTime.SEND.value)

        otp_obj = OneTimePassword.objects.filter(
            otp_type=OTPType.EMAIL.value,
            email=email,
            otp_action=otp_action,
            last_send__gte=past_time,
            is_used=False,
        ).last()

        if not otp_obj:
            otp_obj = OneTimePassword.objects.create(
                otp_type=OTPType.EMAIL.value,
                email=email,
                otp_action=otp_action,
            )

        try:
            otp, signature = require_new_otp(otp_obj, interval=interval)
            """Send mail"""
            send_email_verification_otp_by_email_template.s(
                email,
                "verification step",
                otp,
                interval,
            ).apply_async()
            return Response(
                {
                    "message": "success",
                    "verification_id": signature,
                },
                status=HTTP_200_OK,
            )
        except LimitedError:
            raise_throttled(IntervalLockTime.SEND)


class SendValidateEmailVerificationCode(EmailVerificationCodeBaseView):
    operation_description = ("Validate email verification code",)
    responses = (
        {
            HTTP_200_OK: "Send verification success",
            HTTP_400_BAD_REQUEST: "Email is invalid",
            HTTP_500_INTERNAL_SERVER_ERROR: "Server error",
        },
    )
    request_body = (SendEmailVerificationCodeSerializer,)

    def post(self, request):
        return super().post(request)


class ValidateEmailVerificationCode(APIView):
    serializer = ValidateEmailVerificationCodeSerializer
    permission_classes = ()

    operation_description = ("Validate email verification code",)
    responses = (
        {
            HTTP_200_OK: "Verification code is valid",
            HTTP_400_BAD_REQUEST: "Verification code is invalid",
            HTTP_404_NOT_FOUND: "expired",
        },
    )
    request_body = (ValidateEmailVerificationCodeSerializer,)

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
            raise exceptions.NotFound("Expired OTP", "OTP_NOT_FOUND")
        try:
            interval = int(settings.EMAIL_VERIFICATION_CODE_TIMEOUT)
            if not is_valid_otp_instance(instance, code, interval):
                raise exceptions.ParseError("Invalid OTP.", "OTP_INVALID")
        except LimitedError:
            raise_throttled(IntervalLockTime.CHECK)

        if not instance.is_verified:
            instance.is_verified = True
            instance.save()

        return Response(
            {
                "message": "valid",
                "verification_id": signature,
            },
            status=HTTP_200_OK,
        )
