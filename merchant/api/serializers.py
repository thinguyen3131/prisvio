from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from merchant.models import Merchant


class MerchantPreviewSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(read_only=True)

    class Meta:
        model = Merchant
        fields = ('id', 'name', 'description', 'timezone', 'email', 'phone_number',
                  'website', 'is_active', 'uid', 'latitude', 'longitude', 'location',
                  'created_at', 'updated_at')
        read_only_fields = fields


class MerchantSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(required=False)

    class Meta:
        model = Merchant
        fields = ('id', 'name', 'description', 'timezone', 'email', 'phone_number',
                  'website', 'is_active', 'uid', 'latitude', 'longitude', 'location',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
