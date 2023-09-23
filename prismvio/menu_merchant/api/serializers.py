from rest_framework import serializers

from prismvio.menu_merchant.models import Category, Hashtag, Products, Promotion, Services
from prismvio.merchant.models import Merchant


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = "__all__"


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True)
    promotion_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

    class Meta:
        model = Products
        fields = "__all__"

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        product = Products.objects.create(**validated_data)

        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    product.hashtags.add(hashtag)
        if promotion_ids:
            for promotion_data in promotion_ids:
                print(promotion_data)
                promotion = Promotion.objects.get(id=promotion_data)
                promotion.products.add(product)

        return product

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        instance = super().update(instance, validated_data)
        instance.hashtags.clear()
        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    instance.hashtags.add(hashtag)

        # Check if 'promotion' is provided in the data
        if promotion_ids:
            instance.promotions.clear()
            for promotion_id in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_id)
                instance.promotions.add(promotion)

        return instance


class ServiceSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True)
    promotion_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

    class Meta:
        model = Services
        fields = "__all__"

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        service = Services.objects.create(**validated_data)

        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    service.hashtags.add(hashtag)
        if promotion_ids:
            for promotion_data in promotion_ids:
                print(promotion_data)
                promotion = Promotion.objects.get(id=promotion_data)
                promotion.services.add(service)

        return service

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        instance = super().update(instance, validated_data)
        instance.hashtags.clear()
        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    instance.hashtags.add(hashtag)

        # Check if 'promotion' is provided in the data
        if promotion_ids:
            instance.promotions.clear()
            for promotion_id in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_id)
                instance.promotions.add(promotion)

        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = "__all__"


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"


class SearchMerchantSerializer(serializers.ModelSerializer):
    # Khai báo trường promotion lớn nhất và 4 products, services mới nhất
    max_discount_promotion = serializers.SerializerMethodField()
    latest_products = serializers.SerializerMethodField()
    latest_services = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = [
            "id",
            "owner",
            "name",
            "description",
            "email",
            "phone_number",
            "country_code",
            "country_number",
            "platform_number",
            "website",
            "timezone",
            "currency",
            "uid",
            "latitude",
            "longitude",
            "address",
            "is_active",
            "hashtags",
            "categories",
            "keywords",
            "country",
            "province",
            "district",
            "ward",
            "is_staffs_visible",
            "total_available_slot",
            "total_available_slots_unit",
            "total_bookings",
            "max_discount_promotion",
            "latest_products",
            "latest_services",
        ]

    def get_max_discount_promotion(self, obj):
        # Lọc ra promotion có discount lớn nhất
        max_discount_promotion = Promotion.objects.filter(merchant=obj).order_by("-discount").first()
        return PromotionSerializer(max_discount_promotion).data if max_discount_promotion else None

    def get_latest_products(self, obj):
        # Lấy 4 products được tạo mới nhất
        products = obj.products.order_by("-created_at")[:4]
        return ProductsSerializer(products, many=True).data

    def get_latest_services(self, obj):
        # Lấy 4 services được tạo mới nhất
        services = obj.service.order_by("-created_at")[:4]
        return ServicesSerializer(services, many=True).data
