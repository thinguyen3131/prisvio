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
    path("me/", views.MyProfileView.as_view(), name="user-me"),
    path("me/password/", views.MyPasswordView.as_view(), name="user-me-password"),
    path("exists/", views.UserExistsAPIView.as_view(), name="users-exists"),
    path("deactivate/", views.DeactivateAPIView.as_view(), name="deactivate-user"),
    path("privacy-setting/<int:pk>/", views.PrivacySettingAPIView.as_view(), name="privacy-setting"),
]
