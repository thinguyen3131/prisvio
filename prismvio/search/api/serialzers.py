from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from prismvio.menu_merchant.models import Category
from prismvio.merchant.models import Merchant
from prismvio.utils import haversine


def validate_latitude(value):
    """
    Custom validator to validate latitude coordinates.
    """
    if not -90 <= value <= 90:
        raise ValidationError("Latitude must be between -90 and 90 degrees.")


def validate_longitude(value):
    """
    Custom validator to validate longitude coordinates.
    """
    if not -180 <= value <= 180:
        raise ValidationError("Longitude must be between -180 and 180 degrees.")


class IdsQueryParam(serializers.ListField):
    child = serializers.IntegerField(allow_null=False, min_value=1)

    def get_value(self, value):
        result = []
        input_string = value.get(self.field_name)
        if input_string:
            numbers = input_string.split(",")
            for num in numbers:
                try:
                    integer = int(num)
                    if integer and integer > 0:
                        result.append(integer)
                except ValueError:
                    serializers.ValidationError(f"'{num}' is not a valid integer")

        return result


class MerchantQueryParamsSerializer(serializers.Serializer):
    search_text = serializers.CharField(required=True)
    latitude = serializers.FloatField(
        required=False, default=settings.DEFAULT_LATITUDE, validators=[validate_latitude]
    )
    longitude = serializers.FloatField(
        required=False, default=settings.DEFAULT_LONGITUDE, validators=[validate_longitude]
    )
    country_id = serializers.IntegerField(min_value=1, required=False)
    province_id = serializers.IntegerField(min_value=1, required=False)
    district_id = serializers.IntegerField(min_value=1, required=False)
    ward_id = serializers.IntegerField(min_value=1, required=False)
    user_id = serializers.IntegerField(min_value=1, required=False)
    category_ids = IdsQueryParam(required=False, allow_null=False, allow_empty=True)
    distance = serializers.IntegerField(min_value=0, max_value=100, required=False)
    offset = serializers.IntegerField(min_value=0, required=False)
    limit = serializers.IntegerField(min_value=10, max_value=50, required=False)

    def validate_category_ids(self, category_ids):
        for category_id in category_ids:
            if not Category.objects.filter(pk=category_id).exists():
                raise serializers.ValidationError(f"The category not found: {category_id}")

        return category_ids

    def validate(self, attr):
        return attr


class SearchMerchantSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True, read_only=True)
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = "__all__"

    def get_distance(self, obj: Merchant):
        user_position = self.context.get("position")
        if user_position and obj.latitude and obj.longitude:
            latitude = user_position.get("latitude")
            longitude = user_position.get("longitude")
            if latitude and longitude:
                return haversine(latitude, longitude, obj.latitude, obj.longitude)

        return None
