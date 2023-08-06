from rest_framework import serializers
from merchant.models import Merchant
from timezone_field.rest_framework import TimeZoneSerializerField

class MerchantSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField()
    class Meta:
        model = Merchant
        fields = '__all__'