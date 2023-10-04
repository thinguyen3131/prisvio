from django.db.models import Max, Q
from rest_framework import serializers

from prismvio.menu_merchant.models import (
    Category,
    Collection,
    CollectionItem,
    Hashtag,
    Keyword,
    Product,
    Promotion,
    Service,
)
from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__"


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = "__all__"


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, required=False, allow_null=True)
    keywords = KeywordSerializer(many=True, required=False, allow_null=True)
    promotion_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

    class Meta:
        model = Product
        fields = "__all__"

    def validate_original_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("The original price must be equal or greater than zero")
        return value

    def validate_discount_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("The discount price must be equal or greater than  zero")
        return value

    def validate_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("The quantity must be greater than zero")
        return value

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        keywords = validated_data.pop("keywords", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        product = Product.objects.create(**validated_data)

        if keywords:
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    product.keywords.add(key)

        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    product.hashtags.add(hashtag)
        if promotion_ids:
            for promotion_data in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_data)
                promotion.products.add(product)

        return product

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags", None)
        keywords = validated_data.pop("keywords", None)
        promotion_ids = validated_data.pop("promotion_ids", None)
        instance = super().update(instance, validated_data)

        if keywords is not None:
            instance.keywords.clear()
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    instance.keywords.add(key)

        if hashtags_data is not None:
            instance.hashtags.clear()
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    instance.hashtags.add(hashtag)

        # Check if 'promotion' is provided in the data
        if promotion_ids is not None:
            instance.promotions.clear()
            for promotion_id in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_id)
                instance.promotions.add(promotion)

        return instance


class ServiceSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(many=True, required=False, allow_null=True)
    keywords = KeywordSerializer(many=True, required=True, allow_null=True)
    promotion_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    staff_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)

    class Meta:
        model = Service
        fields = "__all__"

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags", [])
        keywords = validated_data.pop("keywords", [])
        promotion_ids = validated_data.pop("promotion_ids", [])
        staff_ids = validated_data.pop("staff_ids", [])

        service = Service.objects.create(**validated_data)

        if keywords:
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    service.keywords.add(key)

        if hashtags_data:
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    service.hashtags.add(hashtag)
        if promotion_ids:
            for promotion_data in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_data)
                promotion.services.add(service)

        if staff_ids:
            for staff_data in staff_ids:
                staff = Staff.objects.get(id=staff_data)
                service.staff.add(staff)

        return service

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags", None)
        keywords = validated_data.pop("keywords", None)
        promotion_ids = validated_data.pop("promotion_ids", None)
        staff_ids = validated_data.pop("staff_ids", None)

        instance = super().update(instance, validated_data)

        if keywords is not None:
            instance.keywords.clear()
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    instance.keywords.add(key)

        if hashtags_data is not None:
            instance.hashtags.clear()
            for hashtag_data in hashtags_data:
                hashtag_name = hashtag_data.get("name")
                if hashtag_name:
                    hashtag, _ = Hashtag.objects.get_or_create(name=hashtag_name)
                    instance.hashtags.add(hashtag)

        # Check if 'promotion' is provided in the data
        if promotion_ids is not None:
            instance.promotions.clear()
            for promotion_id in promotion_ids:
                promotion = Promotion.objects.get(id=promotion_id)
                instance.promotions.add(promotion)

        if staff_ids is not None:
            instance.staff.clear()
            for staff_data in staff_ids:
                staff = Staff.objects.get(id=staff_data)
                instance.staff.add(staff)
        else:
            if instance.staff.exists():
                instance.staff.clear()

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
        model = Product
        fields = "__all__"


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class SearchMerchantSerializer(serializers.ModelSerializer):
    # Declare the largest promotion field and the 4 newest products and services
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
        # Filter out the promotion with the biggest discount
        max_discount_promotion = Promotion.objects.filter(merchant=obj).order_by("-discount").first()
        return PromotionSerializer(max_discount_promotion).data if max_discount_promotion else None

    def get_latest_products(self, obj):
        # Get the 4 most recently created products
        products = obj.products.order_by("-created_at")[:4]
        return ProductsSerializer(products, many=True).data

    def get_latest_services(self, obj):
        # Get the 4 most recently created services
        services = obj.services.order_by("-created_at")[:4]
        return ServicesSerializer(services, many=True).data


class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = ("id", "collection", "product", "service", "order")


class CollectionSerializer(serializers.ModelSerializer):
    product = serializers.ListField(write_only=True)
    service = serializers.ListField(write_only=True)
    merchant_id = serializers.IntegerField(write_only=True)
    collectionitem_set = CollectionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = (
            "id",
            "name",
            "order",
            "product",
            "service",
            "merchant",
            "deleted_at",
            "created_at",
            "updated_at",
            "merchant_id",
            "collectionitem_set",
        )

    def create(self, validated_data):
        product_data = validated_data.pop("product", [])
        service_data = validated_data.pop("service", [])
        merchant_id = validated_data.get("merchant_id")

        if merchant_id and Collection.objects.filter(merchant_id=merchant_id).exists():
            max_order = Collection.objects.filter(merchant_id=merchant_id).aggregate(Max("order"))["order__max"]
            validated_data["order"] = max_order + 1 if max_order is not None else 1
        else:
            validated_data["order"] = 1

        collection = Collection.objects.create(**validated_data)

        for product_item in product_data:
            CollectionItem.objects.create(
                collection=collection, product_id=product_item["id"], order=product_item["order"]
            )

        for service_item in service_data:
            CollectionItem.objects.create(
                collection=collection, service_id=service_item["id"], order=service_item["order"]
            )

        return collection

    def update(self, instance, validated_data):
        product_data = validated_data.pop("product", [])
        service_data = validated_data.pop("service", [])

        instance.name = validated_data.get("name", instance.name)

        instance.save()
        instance.collectionitem_set.all().delete()
        for product_item in product_data:
            CollectionItem.objects.create(
                collection=instance, product_id=product_item["id"], order=product_item["order"]
            )

        for service_item in service_data:
            CollectionItem.objects.create(
                collection=instance, service_id=service_item["id"], order=service_item["order"]
            )

        return instance


class CollectionItemLimitSerializer(serializers.ModelSerializer):
    product = ProductsSerializer(read_only=True)
    service = ServicesSerializer(read_only=True)

    class Meta:
        model = CollectionItem
        fields = ("id", "collection", "product", "service", "order")


class CollectionLimitSerializer(serializers.ModelSerializer):
    total_item = serializers.IntegerField()
    merchant_id = serializers.IntegerField(write_only=True)
    collection_items = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = (
            "id",
            "name",
            "order",
            "merchant",
            "deleted_at",
            "created_at",
            "updated_at",
            "merchant_id",
            "total_item",
            "collection_items",
        )

    # TODO refactor this method
    def get_collection_items(self, obj):
        limit = self.context.get("limit", None)
        where = Q(product__deleted_at__isnull=True).add(Q(product__hidden=False), Q.AND)
        where |= Q(service__deleted_at__isnull=True).add(Q(service__hidden=False), Q.AND)
        # exclude_where = Q(product__hidden=True)
        items = (
            CollectionItem.objects.select_related("product", "service")
            .filter(collection=obj)
            .filter(where)
            .order_by("order")
        )
        if limit > 0:
            items = items[:limit]
        return CollectionItemLimitSerializer(items, many=True).data
