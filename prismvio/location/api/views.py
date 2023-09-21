from copy import deepcopy

from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import AllowAny

from prismvio.location.api.serializers import DistrictSerializer, ProvinceSerializer, WardSerializer, CountrySerializer
from prismvio.location.models import District, Province, Ward, Country
from prismvio.utils.drf_utils import search


class CountryListAPIView(generics.ListAPIView):
    serializer_class = CountrySerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get('updated_at')
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
        updated_at = query_params.get('updated_at')
        country_id = query_params.get('country_id')
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
        updated_at = query_params.get('updated_at')
        country_id = query_params.get('country_id')
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
        updated_at = query_params.get('updated_at')
        country_id = query_params.get('country_id')
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if country_id:
            where &= Q(country_id=country_id)
        queryset = Ward.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=Ward, exclude_fields=["updated_at"])
