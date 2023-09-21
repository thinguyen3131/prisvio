# search.urls.py

from django.urls import path

from prismvio.search.api.views import MerchantSearchView

urlpatterns = [path("merchants/", MerchantSearchView.as_view(), name="merchant-search-view")]
