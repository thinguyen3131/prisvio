from copy import deepcopy
from datetime import datetime

from django.db.models import Count, F, Q
from geopy.distance import geodesic
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prismvio.core.permissions import IsGetPermission
from prismvio.menu_merchant.api.serializers import (
    CategorySerializer,
    CollectionLimitSerializer,
    CollectionSerializer,
    HashtagSerializer,
    MerchantSerializer,
    ProductSerializer,
    ProductsSerializer,
    PromotionSerializer,
    ServiceSerializer,
    ServicesSerializer,
)
from prismvio.menu_merchant.models import Category, Collection, Hashtag, Product, Promotion, Service
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
        merchant_id = query_params.get("merchant_id")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if merchant_id:
            where &= Q(merchant_id=merchant_id)
        queryset = Promotion.objects.select_related("merchant").filter(where)
        return search(queryset=queryset, query_params=query_params, model=Promotion, exclude_fields=["updated_at"])

    def create(self, request, *args, **kwargs):
        all_day = request.data.get("all_day", False)

        if all_day:
            products = Product.objects.filter(hidden=False, deleted_at__isnull=True)
            services = Service.objects.filter(hidden=False, deleted_at__isnull=True)

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
                product = Product.objects.filter(id=product_id, hidden=False, deleted_at__isnull=True).first()
                if product:
                    promotion.products.add(product)

            for service_id in services:
                service = Service.objects.filter(id=service_id, hidden=False, deleted_at__isnull=True).first()
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

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        merchant_id = query_params.get("merchant_id")
        skip_deleted_at = int(query_params.get("skip_deleted_at", 0))
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if merchant_id:
            where &= Q(merchant_id=merchant_id)
        if skip_deleted_at:
            where &= Q(deleted_at__isnull=True)
        queryset = Product.objects.select_related("merchant").filter(where)
        return search(queryset=queryset, query_params=query_params, model=Product, exclude_fields=["updated_at"])

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsGetPermission]

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.now()
        instance.updated_at = datetime.now()
        instance.save()


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsGetPermission]

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        merchant_id = query_params.get("merchant_id")
        skip_deleted_at = int(query_params.get("skip_deleted_at", 0))
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if merchant_id:
            where &= Q(merchant_id=merchant_id)
        if skip_deleted_at:
            where &= Q(deleted_at__isnull=True)
        queryset = Service.objects.select_related("merchant").filter(where)
        return search(
            queryset=queryset, query_params=query_params, model=Service, exclude_fields=["updated_at", "merchant"]
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsGetPermission]

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.now()
        instance.updated_at = datetime.now()
        instance.save()
        instance.staff.clear()


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsGetPermission]

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        updated_at = query_params.get("updated_at")
        where = Q()
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        queryset = Category.objects.filter(where)
        return search(queryset=queryset, query_params=query_params, model=Category, exclude_fields=["updated_at"])


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsGetPermission]

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.now()
        instance.updated_at = datetime.now()
        instance.merchants.clear()
        instance.save()


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


class CreateCollectionView(APIView):
    permission_classes = [IsGetPermission]

    def post(self, request, *args, **kwargs):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionUpdateView(APIView):
    permission_classes = [IsGetPermission]

    def put(self, request, pk, *args, **kwargs):
        try:
            collection = Collection.objects.get(pk=pk)
        except Collection.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionSortView(APIView):
    permission_classes = [IsGetPermission]

    def post(self, request, *args, **kwargs):
        sorted_collection_data = request.data.get("sorted_collection_ids", [])
        merchant_id = request.data.get("merchant_id")

        if not sorted_collection_data or merchant_id is None:
            return Response(
                {"error": "sorted_collections and merchant_id are required."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create a mapping of collection IDs to their new order
        new_order_mapping = {str(item["id"]): item["order"] for item in sorted_collection_data}

        # Fetch collections for the specified merchant
        collections = Collection.objects.filter(merchant_id=merchant_id)

        # Update collection orders based on the mapping
        for collection in collections:
            new_order = new_order_mapping.get(str(collection.id))
            if new_order is not None:
                collection.order = new_order
                collection.save()

        serializer = CollectionSerializer(collections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CollectionListView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        merchant_id = request.query_params.get("merchant_id")
        updated_at = request.query_params.get("updated_at")
        if merchant_id is None:
            return Response({"error": "merchant_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        where = Q(merchant_id=merchant_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        collections = Collection.objects.filter(where)
        collection_serializer = CollectionSerializer(collections, many=True)

        data = {
            "collections": collection_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)


class CollectionDetailView(APIView):
    permission_classes = [IsGetPermission]

    def get(self, request, collection_id, *args, **kwargs):
        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)

        collection_serializer = CollectionSerializer(collection)
        collection_data = collection_serializer.data

        return Response(collection_data, status=status.HTTP_200_OK)

    def delete(self, request, collection_id, *args, **kwargs):
        try:
            collection = Collection.objects.get(id=collection_id)
        except Collection.DoesNotExist:
            return Response({"error": "Collection not found."}, status=status.HTTP_404_NOT_FOUND)
        collection.deleted_at = datetime.now()
        collection.updated_at = datetime.now()
        collection.save()
        return Response(status=status.HTTP_200_OK)


class CollectionLimitListView(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        merchant_id = request.query_params.get("merchant_id")
        updated_at = request.query_params.get("updated_at")
        limit = request.query_params.get("limit", None)
        context = {}
        if limit:
            context = {"limit": int(limit)}

        if merchant_id is None:
            return Response({"error": "merchant_id parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        where = Q(merchant_id=merchant_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)

        collections = Collection.objects.filter(where).annotate(total_item=Count("collectionitem")).order_by("order")
        collection_serializer = CollectionLimitSerializer(collections, many=True, context=context)

        data = {
            "collections": collection_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)
