from rest_framework import serializers

from location.models import District, Province, Ward


class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ("id", "code", "zip_code", "name_vi", "name_en", "created_at", "updated_at", "deleted_at")


class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = ("id", "code", "zip_code", "name_vi", "name_en", "created_at", "updated_at", "deleted_at")


class ProvinceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Province
        fields = ("id",  "code", "zip_code", "name_vi", "name_en", "created_at", "updated_at", "deleted_at")
