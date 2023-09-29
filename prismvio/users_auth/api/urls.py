from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.users_auth.api.views import (
    EmailPasswordResetView,
    LoginAPIView,
    PhonePasswordResetView,
    PrismTokenRefreshView,
    SignupAPIView,
    ValidateEmailVerificationCode,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/token/", PrismTokenRefreshView.as_view(), name="refresh token"),
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("phone/password/reset/", PhonePasswordResetView.as_view(), name="phone-password-reset"),
    path("email/password/reset/", EmailPasswordResetView.as_view(), name="email-password-reset"),
    path("email/validate/otp/", ValidateEmailVerificationCode.as_view(), name="validate-email-otp"),
]
