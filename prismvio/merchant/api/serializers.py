from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from prismvio.location.models import Country, District, Province, Ward
from prismvio.menu_merchant.models import Category, Keyword
from prismvio.merchant.exceptions import MerchantAlreadyExistsException
from prismvio.merchant.models import ExclusionDate, Merchant, TimeslotCollectionMerchant


class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "full_name_vi", "full_name_en")


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ("id", "code", "zip_code", "name_vi", "name_en")


class MerchantSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, required=False)
    timezone = TimeZoneSerializerField(use_pytz=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, allow_null=True, write_only=True
    )

    class Meta:
        model = Merchant
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        if user.merchants.exists():
            raise MerchantAlreadyExistsException()
        category_ids = validated_data.pop("category_ids", [])
        keywords = validated_data.pop("keywords", [])
        merchant = Merchant.objects.create(**validated_data)
        if keywords:
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    merchant.keywords.add(key)

        if category_ids:
            merchant.categories.set(category_ids)
        return merchant

    def update(self, instance, validated_data):
        category_ids = validated_data.pop("category_ids", None)
        keywords = validated_data.pop("keywords", None)
        instance = super().update(instance, validated_data)
        if category_ids is not None:
            instance.categories.set(category_ids)

        if keywords is not None:
            instance.keywords.clear()
            for keyword in keywords:
                name = keyword.get("name")
                if name:
                    key, _ = Keyword.objects.get_or_create(name=name)
                    instance.keywords.add(key)
        return instance


class MerchantPreviewSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    country = CountrySerializer(read_only=True)
    province = ProvinceSerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    ward = WardSerializer(read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)

    class Meta:
        model = Merchant
        fields = "__all__"
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
