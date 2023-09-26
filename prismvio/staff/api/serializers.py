from django.db import transaction
from rest_framework import serializers

from prismvio.staff.enums import InviteStatusEnum, LinkStatusEnum
from prismvio.staff.models import Staff
from prismvio.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "email", "country_code")


class LinkToStaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField()

    class Meta:
        model = Staff
        fields = ("user", "user_id", "invite_status", "link_status")

    def update(self, instance, validated_data):
        validated_data["invite_status"] = InviteStatusEnum.PENDING.value
        validated_data["link_status"] = LinkStatusEnum.UNLINKED.value
        # TODO send notification or email
        return super().update(instance, validated_data)


class StaffAcceptedInviteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = ("user", "invite_status", "link_status")

    def update(self, instance, validated_data):
        if (
            instance.invite_status != InviteStatusEnum.ACCEPTED.value
            and instance.link_status != LinkStatusEnum.LINKED.value
        ):
            validated_data["invite_status"] = InviteStatusEnum.ACCEPTED.value
            validated_data["link_status"] = LinkStatusEnum.LINKED.value
            # create_staff_booking_event_task.delay(staff_id=instance.pk, user_id=instance.user.pk)
            # TODO send notification or email
            return super().update(instance, validated_data)
        return instance


class CancelInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ("user", "invite_status", "link_status")

    def update(self, instance, validated_data):
        validated_data["user"] = None
        validated_data["invite_status"] = None
        validated_data["link_status"] = LinkStatusEnum.UNLINKED.value
        # TODO send notification or email
        return super().update(instance, validated_data)


class UnlinkStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ("user", "invite_status", "link_status")

    def update(self, instance, validated_data):
        validated_data["user"] = None
        validated_data["invite_status"] = None
        validated_data["link_status"] = LinkStatusEnum.UNLINKED.value
        # TODO send notification or email
        return super().update(instance, validated_data)


class StaffSerializer(serializers.ModelSerializer):
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    service = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user = UserSerializer(read_only=True, required=False, allow_null=True)
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Staff
        extra_kwargs = {
            "name": {"required": True},
            "phone_number": {"required": True},
            "merchant": {"required": True},
        }
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "deleted_at")

    def validate_email(self, value):
        if value:
            queryset = Staff.objects.filter(email=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("The email exists")
        return value

    def validate_phone_number(self, value):
        if value:
            queryset = Staff.objects.filter(phone_number=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("The phone number exists")
        return value

    def validate_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The price must be greater or equal than zero.")
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        if not email and not phone_number:
            raise serializers.ValidationError("Email and phone number can not be null.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        if "user" in validated_data and validated_data["user"]:
            validated_data["invite_status"] = InviteStatusEnum.PENDING.value
            validated_data["link_status"] = LinkStatusEnum.UNLINKED.value
        if "service_ids" in validated_data:
            service_ids = validated_data.pop("service_ids")
            staff = super().create(validated_data)
            if service_ids:
                staff.service.set(service_ids)
            return staff
        else:
            return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        if "service_ids" in validated_data:
            service_ids = validated_data.pop("service_ids")
            staff = super().update(instance, validated_data)
            staff.service.set(service_ids)
            return staff
        else:
            return super().update(instance, validated_data)
