import pytest
from rest_framework.test import APIRequestFactory

from prismvio.api.users.views import UserViewSet
from prismvio.users.models import User


class TestUserViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()
