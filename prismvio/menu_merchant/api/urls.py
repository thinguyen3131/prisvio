from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.menu_merchant.api.views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    HashtagListCreateView,
    HashtagRetrieveUpdateDestroyView,
    ParentIDListView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    PromotionListCreateView,
    PromotionRetrieveUpdateDestroyView,
    ServiceListCreateView,
    ServiceRetrieveUpdateDestroyView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# menu_merchant
urlpatterns = [
    path("hashtags/", HashtagListCreateView.as_view(), name="hashtag-list-create"),
    path("hashtags/<int:pk>/", HashtagRetrieveUpdateDestroyView.as_view(), name="hashtag-detail"),
    path("promotions/", PromotionListCreateView.as_view(), name="promotion-list-create"),
    path("promotions/<int:pk>/", PromotionRetrieveUpdateDestroyView.as_view(), name="promotion-detail"),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductRetrieveUpdateDestroyView.as_view(), name="product-detail"),
    path("services/", ServiceListCreateView.as_view(), name="service-list-create"),
    path("services/<int:pk>/", ServiceRetrieveUpdateDestroyView.as_view(), name="service-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"),
    path("parent_ids/", ParentIDListView.as_view(), name="parent-id-list"),
]