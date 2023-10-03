from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.menu_merchant.api.views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    CollectionDetailView,
    CollectionLimitListView,
    CollectionListView,
    CollectionSortView,
    CollectionUpdateView,
    CreateCollectionView,
    GetCategoryData,
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
    path("get_category_data/", GetCategoryData.as_view(), name="get_category_data"),
    path("create_collection/", CreateCollectionView.as_view(), name="create-collection"),
    path("collections/<int:pk>/update/", CollectionUpdateView.as_view(), name="collection-update"),
    path("collections/sort/", CollectionSortView.as_view(), name="collection-sort"),
    path("collections/", CollectionListView.as_view(), name="collection-list"),
    path("collections/<int:collection_id>/", CollectionDetailView.as_view(), name="collection-detail"),
    path("collections/items/", CollectionLimitListView.as_view(), name="a"),
]
