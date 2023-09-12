from rest_framework_simplejwt.views import TokenViewBase

from prismvio.users_auth.api.serializers import LoginSerializer, PrismTokenRefreshSerializer


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
