from rest_framework import generics

from prismvio.menu_merchant.models import Category, Hashtag, Products, Promotion, Services

from ..permissions import IsBusinessAdminOrAdmin
from .serializers import (
    CategorySerializer,
    HashtagSerializer,
    ProductSerializer,
    PromotionSerializer,
    ServiceSerializer,
)


class HashtagListCreateView(generics.ListCreateAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class HashtagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class PromotionListCreateView(generics.ListCreateAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class PromotionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class ServiceListCreateView(generics.ListCreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsBusinessAdminOrAdmin]


class ParentIDListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent_id__isnull=False)
    serializer_class = CategorySerializer
    permission_classes = [IsBusinessAdminOrAdmin]
