from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from prismvio.menu_merchant.models import Category
from prismvio.merchant.exceptions import MerchantAlreadyExistsException
from prismvio.merchant.models import ExclusionDate, Merchant, TimeslotCollectionMerchant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MerchantSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Merchant
        fields = "__all__"

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        if user.merchants.exists():
            raise MerchantAlreadyExistsException()
        return attrs

    def create(self, validated_data):
        category_ids = validated_data.pop("category_ids", [])
        merchant = super().create(validated_data)
        if category_ids:
            merchant.categories.set(category_ids)
        return merchant


class MerchantPreviewSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Merchant
        fields = (
            "id",
            "name",
            "description",
            "timezone",
            "email",
            "phone_number",
            "currency",
            "website",
            "is_active",
            "uid",
            "latitude",
            "longitude",
            "location",
            "categories",
            "created_at",
            "updated_at",
            "total_available_slot",
            "total_available_slots_unit",
            "is_staffs_visible",
        )
        read_only_fields = fields


class ExclusionDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExclusionDate
        fields = "__all__"


class TimeslotCollectionMerchantSerializer(serializers.ModelSerializer):
    exclusion_dates = serializers.SerializerMethodField()

    class Meta:
        model = TimeslotCollectionMerchant
        fields = ("id", "weekly", "daily", "exclusion_dates", "deleted_at", "created_at", "updated_at", "merchant")

    def get_exclusion_dates(self, obj):
        exclusion_dates = ExclusionDate.objects.filter(merchant=obj.merchant)
        if exclusion_dates:
            return ExclusionDateSerializer(exclusion_dates, many=True).data
        return []
