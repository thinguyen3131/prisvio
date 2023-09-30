import logging
from datetime import timedelta

from django.db.models.signals import post_save
from django.db import models
from django.dispatch import receiver
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import exceptions, generics, status, viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from prismvio.core.permissions import IsGetPermission
from prismvio.users.api.serializers import (
    DeactivateUserActiveStatusSerializer,
    MeDetailSerializer,
    PrivacySettingSerializer,
    SendEmailVerificationCodeSerializer,
    SubUserSerializer,
    UpdatePasswordSerializer,
    FriendshipSerializer,
)
from prismvio.users.enums import IntervalLockTime, OTPAction, OTPType
from prismvio.users.models.otp import OneTimePassword
from prismvio.users.models.user import PrivacySetting, Friendship, Friend
from prismvio.users.otp import LimitedError, require_new_otp
from prismvio.users.tasks import send_email_verification_otp_by_email_template

User = get_user_model()

logger = logging.getLogger("django")


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


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MeDetailSerializer

    def get_object(self):
        return self.request.user


class MyPasswordView(generics.UpdateAPIView):
    permission_classes = [IsGetPermission]
    serializer_class = UpdatePasswordSerializer
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user.password = make_password(serializer.data.get("new_password"))
        user.save()

        return Response(status=HTTP_204_NO_CONTENT)


class UserExistsAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        email = request.data.get("email", None)
        phone_number = request.data.get("phone_number", None)
        is_existed = False
        if email:
            is_existed = User.objects.filter(email=email).exists()
        if phone_number:
            is_existed = User.objects.filter(phone_number=phone_number).exists()
        return Response({"is_existed": is_existed}, status=HTTP_200_OK)


class DeactivateAPIView(APIView):
    def post(self, request):
        serializer = DeactivateUserActiveStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        update_success = True
        try:
            payload = jwt.decode(request.auth.token, options={"verify_signature": False})
            user = User.objects.get(pk=payload["user_id"])

            if user.pk != request.user.pk:
                raise ValueError("Cannot change status for other user")

            key = RefreshToken(data.get("refresh_token"))
            key.blacklist()
            user.set_status_active(status=False)
        except (ValueError, User.DoesNotExist) as err:
            logger.error(
                f"Cannot deactivate for user {request.user.email}",
                extra=dict(request_data=request.data, error=str(err)),
            )
            update_success = False
        except (TokenError, jwt.DecodeError) as err:
            logger.error(
                f"Cannot deactivate for user {request.user.email}",
                extra=dict(request_data=request.data, error=str(err)),
            )
            update_success = False
        return JsonResponse(
            {
                "success": update_success,
            },
            status=HTTP_200_OK,
        )


class PrivacySettingAPIView(APIView):
    permission_classes = [IsGetPermission]

    def get_object(self, user_id):
        try:
            return PrivacySetting.objects.get(user_id=user_id)
        except PrivacySetting.DoesNotExist:
            return None

    def get(self, request, user_id, format=None):
        privacy_setting = self.get_object(user_id)
        if privacy_setting:
            serializer = PrivacySettingSerializer(privacy_setting)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        print(request.data)
        serializer = PrivacySettingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, user_id, format=None):
        privacy_setting = self.get_object(user_id)
        if privacy_setting:
            serializer = PrivacySettingSerializer(privacy_setting, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, format=None):
        privacy_setting = self.get_object(user_id)
        if privacy_setting:
            privacy_setting.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class SubUserCreateAPIView(generics.CreateAPIView):
    serializer_class = SubUserSerializer


class SendOTPEmailPasswordResetView(EmailVerificationCodeBaseView):
    def get_otp_action(self):
        return OTPAction.PASSWORD_RESET.value

    def validate_email(self, email):
        try:
            User.objects.get(
                email=email,
            )
        except User.DoesNotExist:
            raise exceptions.NotFound("User not found", "user_not_found")

    def post(self, request):
        return super().post(request)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    
    def create(self, request, *args, **kwargs):
        sender = request.user
        receiver_id = request.data.get('receiver')
        
        if not receiver_id or Friendship.objects.filter(sender=sender, receiver_id=receiver_id).exists():
            return Response({'detail': 'Invalid receiver or Friendship already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={'sender': sender.id, 'receiver': receiver_id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        friendship = self.get_object()
        
        if request.user != friendship.receiver:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        status = request.data.get('status')
        if status not in [Friendship.PENDING, Friendship.ACCEPTED, Friendship.DECLINED]:
            return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        friendship.status = status
        friendship.save()
        
        if status == Friendship.ACCEPTED:
            # Logic to create Friend objects can be handled by the signal as mentioned in the previous response
            pass
        
        serializer = self.get_serializer(friendship)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        friendship = self.get_object()

        if request.user != friendship.sender and request.user != friendship.receiver:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        Friend.objects.filter(
            models.Q(user=friendship.sender, friend=friendship.receiver) | 
            models.Q(user=friendship.receiver, friend=friendship.sender)
        ).delete()
        
        # Xóa đối tượng Friendship
        friendship.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

@receiver(post_save, sender=Friendship)
def create_friend_objects(sender, instance, **kwargs):
    if instance.status == Friendship.ACCEPTED:
        Friend.objects.create(user=instance.sender, friend=instance.receiver)
        Friend.objects.create(user=instance.receiver, friend=instance.sender)