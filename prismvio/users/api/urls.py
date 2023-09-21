from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.users.api.views import SendValidateEmailVerificationCode

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("send_email_otp/", SendValidateEmailVerificationCode.as_view(), name="send-email-otp"),
]