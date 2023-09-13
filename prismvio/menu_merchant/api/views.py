from copy import deepcopy
from datetime import datetime

from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response

from prismvio.core.permissions import IsGetPermission
from prismvio.menu_merchant.api.serializers import (
    CategorySerializer,
    HashtagSerializer,
    ProductSerializer,
    PromotionSerializer,
    ServiceSerializer,
)
from prismvio.menu_merchant.models import Category, Hashtag, Products, Promotion, Services
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
            products = Products.objects.filter(hidden=False, deleted_at=False)
            services = Services.objects.filter(hidden=False, deleted_at=False)

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
                product = Products.objects.filter(id=product_id, hidden=False, deleted_at=False).first()
                if product:
                    promotion.products.add(product)

            for service_id in services:
                service = Services.objects.filter(id=service_id, hidden=False, deleted_at=False).first()
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
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsGetPermission]


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsGetPermission]


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsGetPermission]


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Services.objects.all()
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
