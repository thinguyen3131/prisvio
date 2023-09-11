from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.merchant.api.views import MerchantViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# ViewSets
router.register(r"merchants", MerchantViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

# mechant
urlpatterns += [
    path("merchants/<int:pk>/delete/", MerchantViewSet.as_view({"delete": "delete_merchant"}), name="delete_merchant"),
]
