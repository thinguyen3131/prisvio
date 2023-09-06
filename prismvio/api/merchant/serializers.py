from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from prismvio.merchant.models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(use_pytz=True)

    class Meta:
        model = Merchant
        fields = "__all__"
