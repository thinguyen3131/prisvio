from django.contrib.auth import get_user_model
from rest_framework import serializers

from prismvio.users.models import User as UserType

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = UserModel
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class EmailPhoneLookupSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.CharField(), required=False)
    phones = serializers.ListField(child=serializers.CharField(), required=False)
    link = serializers.CharField(required=False)

    def to_internal_value(self, data):
        for f in ["emails", "phones"]:
            if data.get(f):
                # Get unique elements, preserving order
                data[f] = list(dict.fromkeys(data[f]))
        return super().to_internal_value(data)

    def validate(self, data):
        if not data.get("emails") and not data.get("phones"):
            raise serializers.ValidationError('Fields "emails" or "phones" required.')
        return data


class UserDetailSerializer(serializers.Serializer):
    class Meta:
        model = UserModel
        fields = "__all__"
        read_only_fields = fields
