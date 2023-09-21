from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.merchant.api.views import (
    ExclusionDateAPIVIew,
    MerchantDetailView,
    MerchantListCreateView,
    ShiffsAPIView,
    TimeslotsAPIView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("", MerchantListCreateView.as_view(), name="list-create-merchant"),
    path("<int:merchant_id>/timeslots/", TimeslotsAPIView.as_view(), name="manage_timeslots"),
    path("<int:merchant_id>/timeslots/", TimeslotsAPIView.as_view(), name="manage_timeslots"),
    path("<int:merchant_id>/shifts/", ShiffsAPIView.as_view(), name="manage_shifts"),
    path("<int:merchant_id>/exclusion_dates/", ExclusionDateAPIVIew.as_view(), name="manage_exclusion_dates"),
    path("<int:pk>/", MerchantDetailView.as_view(), name="merchant-detail"),
]
