from django.urls import include, path

from rest_framework_extensions.routers import ExtendedSimpleRouter

from merchant.api.viewsets import MerchantViewSet

router = ExtendedSimpleRouter()

router.register(r'merchants', MerchantViewSet, basename='merchant')

urlpatterns = [
    path('', include(router.urls)),
]
