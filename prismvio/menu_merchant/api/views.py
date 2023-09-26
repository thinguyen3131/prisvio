from copy import deepcopy
from datetime import datetime

from django.db.models import F, Q
from geopy.distance import geodesic
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prismvio.core.permissions import IsGetPermission
from prismvio.menu_merchant.api.serializers import (  # get category for merchant product service
    CategorySerializer,
    HashtagSerializer,
    MerchantSerializer,
    ProductSerializer,
    ProductsSerializer,
    PromotionSerializer,
    ServiceSerializer,
    ServicesSerializer,
)
from prismvio.menu_merchant.models import Category, Hashtag, Product, Promotion, Service
from prismvio.merchant.models import Merchant
from prismvio.utils.drf_utils import search


class HashtagListCreateView(generics.ListCreateAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsGetPermission]


class HashtagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsGetPermission]


class PromotionListCreateView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsGetPermission]

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        queryset = Promotion.objects.select_related("merchant").filter(where)
        return search(queryset=queryset, query_params=query_params, model=Promotion, exclude_fields=["updated_at"])

    def create(self, request, *args, **kwargs):
        all_day = request.data.get("all_day", False)

        if all_day:
            products = Product.objects.filter(hidden=False, deleted_at=False)
            services = Service.objects.filter(hidden=False, deleted_at=False)

            promotion_serializer = self.get_serializer(data=request.data)
            promotion_serializer.is_valid(raise_exception=True)
            promotion = promotion_serializer.save()

            promotion.products.set(products)
            promotion.services.set(services)

            return Response(promotion_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        products = self.request.data.get("products", [])
        services = self.request.data.get("services", [])

        promotion = serializer.save(owner=self.request.user)

        if not promotion.all_day:
            for product_id in products:
                product = Product.objects.filter(id=product_id, hidden=False, deleted_at=False).first()
                if product:
                    promotion.products.add(product)

            for service_id in services:
                service = Service.objects.filter(id=service_id, hidden=False, deleted_at=False).first()
                if service:
                    promotion.services.add(service)


class PromotionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsGetPermission]

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.now()
        instance.updated_at = datetime.now()
        instance.save()


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsGetPermission]


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsGetPermission]


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsGetPermission]


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsGetPermission]


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsGetPermission]


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsGetPermission]


class ParentIDListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent_id__isnull=False)
    serializer_class = CategorySerializer
    permission_classes = [IsGetPermission]


class MerchantListAPIView(generics.ListAPIView):
    serializer_class = MerchantSerializer

    def get_queryset(self):
        queryset = Merchant.objects.filter(categories__id=self.request.query_params.get("category_id"))
        country_code = self.request.query_params.get("country_code")
        province_code = self.request.query_params.get("province_code")
        district_code = self.request.query_params.get("district_code")
        ward_code = self.request.query_params.get("ward_code")
        latitude = self.request.query_params.get("latitude")
        longitude = self.request.query_params.get("longitude")
        radius = float(self.request.query_params.get("radius", 1))  # Default radius is 1 km

        if latitude and longitude:
            queryset = [
                merchant
                for merchant in queryset
                if geodesic((merchant.latitude, merchant.longitude), (latitude, longitude)).kilometers <= radius
            ]

        else:
            if country_code:
                queryset = queryset.filter(country__code=province_code)
            if province_code:
                queryset = queryset.filter(province__code=province_code)
            if district_code:
                queryset = queryset.filter(district__code=district_code)
            if ward_code:
                queryset = queryset.filter(ward__code=ward_code)

        return queryset.annotate(sort_order=F("total_bookings")).order_by("-sort_order", "-created_at")


class ProductsListAPIView(generics.ListAPIView):
    serializer_class = ProductsSerializer

    def get_queryset(self):
        return Product.objects.filter(category__id=self.request.query_params.get("category_id"))


class ServicesListAPIView(generics.ListAPIView):
    serializer_class = ServicesSerializer

    def get_queryset(self):
        return Service.objects.filter(category__id=self.request.query_params.get("category_id"))


class GetCategoryData(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        merchants_view = MerchantListAPIView.as_view()
        products_view = ProductsListAPIView.as_view()
        services_view = ServicesListAPIView.as_view()

        merchants_response = merchants_view(request._request).data
        products_response = products_view(request._request).data
        services_response = services_view(request._request).data

        return Response(
            {"merchants": merchants_response, "products": products_response, "services": services_response}
        )
