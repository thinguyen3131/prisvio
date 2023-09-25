from django.urls import path

from prismvio.social_login.api.views import google_login

urlpatterns = [
    path("login/", google_login, name="google-login"),
]
