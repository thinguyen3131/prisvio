from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.users.api import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("send_email_otp/", views.SendValidateEmailVerificationCode.as_view(), name="send-email-otp"),
    path("send_email_otp/password/reset/", views.SendOTPEmailPasswordResetView.as_view(), name="otp-password-reset"),
    path("me/", views.MyProfileView.as_view(), name="user-me"),
    path("me/password/", views.MyPasswordView.as_view(), name="user-me-password"),
    path("exists/", views.UserExistsAPIView.as_view(), name="users-exists"),
    path("deactivate/", views.DeactivateAPIView.as_view(), name="deactivate-user"),
    path(
        "privacy-settings/", views.PrivacySettingAPIView.as_view(), name="create-privacy-setting"
    ),  # POST: Create a new PrivacySetting
    path(
        "privacy-settings/<int:user_id>/", views.PrivacySettingAPIView.as_view(), name="privacy-setting-crud"
    ),  # GET, PUT, DELETE for specific user's PrivacySetting
    path("subuser/", views.SubUserCreateAPIView.as_view(), name="create-subuser"),
]
