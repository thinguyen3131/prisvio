from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.users_auth.api.views import LoginAPIView, PrismTokenRefreshView

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("refresh/token/", PrismTokenRefreshView.as_view(), name="refresh token"),
]
