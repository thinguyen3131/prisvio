from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import MerchantViewSet

router = DefaultRouter()
router.register(r'merchants', MerchantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('merchants/<int:pk>/delete/', MerchantViewSet.as_view({'delete': 'delete_merchant'}), name='delete_merchant'),
]
