# search.urls.py

from django.urls import path

from prismvio.search.api.views import MerchantSearchView, ProductSearchView, ServiceSearchView

urlpatterns = [
    path("merchants/", MerchantSearchView.as_view(), name="merchant-search-view"),
    path("services/", ServiceSearchView.as_view(), name="service-search-view"),
    path("products/", ProductSearchView.as_view(), name="product-search-view"),
]
