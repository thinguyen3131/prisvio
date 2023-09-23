import csv
from copy import deepcopy

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny

from prismvio.location.api.serializers import CountrySerializer, DistrictSerializer, ProvinceSerializer, WardSerializer
from prismvio.location.models import Country, District, Province, Ward
from prismvio.utils.drf_utils import search


class CountryListAPIView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        queryset = Country.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=Country, exclude_fields=["updated_at"])


class ProvinceListAPIView(generics.ListAPIView):
    serializer_class = ProvinceSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        country_id = query_params.get("country_id")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if country_id:
            where &= Q(country_id=country_id)
        queryset = Province.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=Province, exclude_fields=["updated_at"])


class DistrictListAPIView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        country_id = query_params.get("country_id")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if country_id:
            where &= Q(country_id=country_id)
        queryset = District.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=District, exclude_fields=["updated_at"])


class WardListAPIView(generics.ListAPIView):
    serializer_class = WardSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        country_id = query_params.get("country_id")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if country_id:
            where &= Q(country_id=country_id)
        queryset = Ward.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=Ward, exclude_fields=["updated_at"])


def export_to_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="Country.csv"'

    writer = csv.writer(response)
    writer.writerow(["code", "full_name_vi", "full_name_en", "zip_code", "created_at", "updated_at"])  # header

    for obj in Country.objects.all():
        writer.writerow([obj.code, obj.full_name_vi, obj.full_name_en, obj.zip_code, obj.created_at, obj.updated_at])

    return response
