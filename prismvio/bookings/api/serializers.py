from datetime import datetime

import pytz
from django.db import transaction
from rest_framework import serializers

from prismvio.bookings.enums import BookingStatusEnum
from prismvio.bookings.models import Booking, BookingProduct, BookingPromotion, BookingService
from prismvio.bookings.services.push import PushBookingMessage
from prismvio.bookings.tasks import create_booking_event_task
from prismvio.menu_merchant.models import Product, Promotion, Service


class CancelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "status", "cancel_reason")

    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.status != BookingStatusEnum.CANCELED.value:
            booking_products = BookingProduct.objects.select_related("booking", "product").filter(booking=instance)
            items = booking_products.iterator()
            for item in items:
                product = item.product
                product.quantity = product.quantity + item.quantity
                product.sold_quantity = product.sold_quantity - item.quantity
                product.save()
            instance.status = BookingStatusEnum.CANCELED.value
            instance.cancel_reason = validated_data.get("cancel_reason", "")
            instance.cancel_by = validated_data.get("cancel_by", "")
            instance.save()
        return instance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        exclude = (
            "hashtags",
            "merchant",
            "owner",
            "category",
            "original_price",
            "discount_price",
            "time",
            "time_date",
        )


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ("hashtags", "images", "merchant", "owner")


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        exclude = ("products", "services")


class BookingServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(write_only=True, source="services", queryset=Service.objects.all())

    class Meta:
        model = BookingService
        fields = (
            "id",
            "service",
            "service_id",
            "staff",
            "duration",
            "price",
            "quantity",
            "note",
            "start_date",
            "end_date",
            "is_anyone",
            "service_info",
            "staff_info",
            "merchant_info",
            "user_info",
        )
        extra_kwargs = {
            "start_date": {"required": True},
            "end_date": {"required": True},
        }

    def validate_start_date(self, value):
        if value and value.replace(tzinfo=pytz.UTC) < datetime.now(tz=pytz.UTC):
            raise serializers.ValidationError("The start date must be greater or equal than current date")
        return value

    def validate_end_date(self, value):
        if value and value.replace(tzinfo=pytz.UTC) < datetime.now(tz=pytz.utc):
            raise serializers.ValidationError("The end date must be greater or equal than current date")
        return value

    def validate_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The price must be greater or equal than zero")
        return value

    def validate_quantity(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("The quantity must be greater than zero")
        return value

    def validate_duration(self, value):
        if value and value <= 0:
            raise serializers.ValidationError("The duration must be greater than zero")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("The start date must be less than end date")
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        service = data.pop("service")
        data["service_id"] = service["id"]
        data["name"] = service["name"]
        return data


class BookingProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(write_only=True, source="products", queryset=Product.objects.all())

    class Meta:
        model = BookingProduct
        fields = ("id", "product", "product_id", "quantity", "price", "product_info")

    def validate_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The price must be greater or equal than zero.")
        return value

    def validate_quantity(self, value):
        if value and value < 1:
            raise serializers.ValidationError("The quantity must be greater than zero.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        product = data.pop("product")
        data["product_id"] = product["id"]
        data["name"] = product["name"]
        return data


class BookingPromotionSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    promotion_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="promotion", queryset=Promotion.objects.all()
    )

    class Meta:
        model = BookingPromotion
        fields = ("id", "promotion", "promotion_id", "price", "promotion_info")

    def validate_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The price should greater than zero.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        promotion = data.pop("promotion")
        data["promotion_id"] = promotion["id"]
        data["name"] = promotion["name"]
        return data


class BookingSerializer(serializers.ModelSerializer):
    services = BookingServiceSerializer(source="bookingservice_set", many=True, allow_null=True, required=False)
    products = BookingProductSerializer(source="bookingproduct_set", many=True, allow_null=True, required=False)
    promotions = BookingPromotionSerializer(source="bookingpromotion_set", many=True, allow_null=True, required=False)

    class Meta:
        model = Booking
        fields = "__all__"
        extra_kwargs = {
            "start_date": {"required": True},
            "end_date": {"required": True},
            "merchant": {"required": True},
        }

    def validate_merchant(self, value):
        if value is None:
            raise serializers.ValidationError("The merchant can not null.")
        return value

    def validate_total_price(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The price must be greater or equal than zero.")
        return value

    def validate_duration(self, value):
        if value and value < 0:
            raise serializers.ValidationError("The duration must be greater or equal than zero.")
        return value

    def validate_start_date(self, value):
        if value is None:
            raise serializers.ValidationError("The start date can not null")
        if value < datetime.now().date():
            raise serializers.ValidationError("The start date must be greater or equal than current date.")
        return value

    def validate_end_date(self, value):
        if value is None:
            raise serializers.ValidationError("The end date can not null")
        if value < datetime.now().date():
            raise serializers.ValidationError("The start date must be greater or equal than current date.")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        if start_date > end_date:
            raise serializers.ValidationError("The end date must be greater or equal than start date.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        services = validated_data.pop("bookingservice_set")
        products = validated_data.pop("bookingproduct_set")
        promotions = validated_data.pop("bookingpromotion_set")

        booking = super().create(validated_data)
        user_ids = [booking.merchant.owner.pk]
        if services:
            booking_services = []
            for data in services:
                service = data.pop("services")
                data["booking"] = booking
                data["service"] = service
                staff = data.get("staff", None)
                if staff:
                    user_ids.append(staff.pk)
                # update sold quantity
                quantity = data.get("quantity", 0)
                if quantity:
                    service.sold_quantity += quantity
                    service.save()
                booking_services.append(BookingService(**data))
            BookingService.objects.bulk_create(booking_services)
        if products:
            booking_products = []
            for data in products:
                product = data.pop("products")
                data["booking"] = booking
                data["product"] = product
                booking_products.append(BookingProduct(**data))
                # update product quantity
                quantity = data.get("quantity", 0)
                product.quantity = product.quantity - quantity
                product.sold_quantity = product.sold_quantity + quantity
                if product.quantity < 0:
                    raise serializers.ValidationError("The product does not enough quantity.")
                product.save()
            BookingProduct.objects.bulk_create(booking_products)
        if promotions:
            booking_promotions = []
            for data in promotions:
                promotion = data.pop("promotion")
                data["booking"] = booking
                data["promotion"] = promotion
                booking_promotions.append(BookingPromotion(**data))
            BookingPromotion.objects.bulk_create(booking_promotions)
        create_booking_event_task.delay(BookingSerializer(booking).data)
        PushBookingMessage(booking).send(user_ids)
        return booking
