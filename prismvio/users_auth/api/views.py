from rest_framework_simplejwt.views import TokenViewBase
from prismvio.users_auth.api.serializers import LoginSerializer


class LoginAPIView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    It's similar to TokenObtainPairView from rest_framework_simplejwt package
    but uses custom serializer class
    """
    serializer_class = LoginSerializer
