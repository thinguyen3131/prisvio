from typing import Any

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from prismvio.menu_merchant.models import Service
from prismvio.merchant.api.serializers import MerchantSerializer
from prismvio.merchant.models import Merchant
from prismvio.search.api.serialzers import MerchantQueryParamsSerializer, SearchMerchantSerializer, SearchServiceSerializer, ServiceQueryParamsSerializer
from prismvio.search.documents.merchant import MerchantSearch, MerchantSearchRequest
from prismvio.search.documents.service import ServiceSearchRequest, ServiceSearch


class SearchBaseView(GenericAPIView):
    permission_classes = []
    queryset = Merchant.objects.filter()
    serializer_class = MerchantSerializer
    query_params_serializer_class = None
    search_request_class = None
    search_class = None

    def get_serializer_context(self) -> dict[str, Any]:
        context = super().get_serializer_context()
        if self.request.query_params:
            longitude = self.request.query_params.get("longitude", None)
            latitude = self.request.query_params.get("latitude", None)
            if longitude and latitude:
                context.update(
                    {
                        "position": {
                            "latitude": float(latitude),
                            "longitude": float(longitude),
                        }
                    }
                )
        return context

    def get_query_params_serializer_class(self):
        assert self.query_params_serializer_class is not None, (
            "'%s' should either include a `query_params_serializer_class` attribute, "
            "or override the `get_query_params_serializer_class()` method." % self.__class__.__name__
        )

        return self.query_params_serializer_class

    def get_search_request_class(self):
        assert self.search_request_class is not None, (
            "'%s' should either include a `search_request_class` attribute, "
            "or override the `get_search_request_class()` method." % self.__class__.__name__
        )

        return self.search_request_class

    def get_search_class(self):
        assert self.search_class is not None, (
            "'%s' should either include a `search_class` attribute, "
            "or override the `get_search_class()` method." % self.__class__.__name__
        )

        return self.search_class

    def get(self, request):
        query_params_serializer_class = self.get_query_params_serializer_class()
        search_class = self.get_search_class()
        search_request_class = self.get_search_request_class()

        request_params_serializer = query_params_serializer_class(data=request.query_params)
        request_params_serializer.is_valid(raise_exception=True)

        search_instance = search_class()
        queryset = self.get_queryset()
        search_request = search_request_class.model_validate(request_params_serializer.validated_data)
        result, total = search_instance.custom_search(queryset, search_request)
        serializer = self.get_serializer(result, many=True)

        return Response(
            {
                "total": total,
                "items": serializer.data,
            }
        )


class MerchantSearchView(SearchBaseView):
    permission_classes = []
    queryset = Merchant.objects.filter()
    serializer_class = SearchMerchantSerializer

    query_params_serializer_class = MerchantQueryParamsSerializer
    search_request_class = MerchantSearchRequest
    search_class = MerchantSearch


class ServiceSearchView(SearchBaseView):
    permission_classes = []
    queryset = Service.objects.filter()
    serializer_class = SearchServiceSerializer

    query_params_serializer_class = ServiceQueryParamsSerializer
    search_request_class = ServiceSearchRequest
    search_class = ServiceSearch
