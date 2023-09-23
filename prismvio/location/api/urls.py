from django.urls import path

from prismvio.location.api import views

urlpatterns = [
    path("locations/countries/", views.CountryListAPIView.as_view(), name="list-countries"),
    path("locations/provinces/", views.ProvinceListAPIView.as_view(), name="list-provinces"),
    path("locations/districts/", views.DistrictListAPIView.as_view(), name="list-districts"),
    path("locations/wards/", views.WardListAPIView.as_view(), name="list-wards"),
    path("export-csv/", views.export_to_csv, name="export_to_csv"),
]
