from django.conf import settings
from django.db import models
from django.db.models import JSONField

from prismvio.bookings.enums import BookingStatusEnum, PaymentMethodEnum
from prismvio.menu_merchant.models import Products, Promotion, Services
from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff


class Booking(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True, blank=True)
    booked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booked_user",
        default=None,
    )
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="booked_by",
        default=None,
    )
    start_date = models.DateField(null=True, blank=True, default=None)
    end_date = models.DateField(null=True, blank=True, default=None)
    total_price = models.FloatField(null=True, blank=True, default=None)
    note = models.TextField(null=True, blank=True, default=None)
    status = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=BookingStatusEnum.choices(),
        default=BookingStatusEnum.UPCOMING.value,
    )
    payment_method = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=PaymentMethodEnum.choices(),
        default=PaymentMethodEnum.CASH.value,
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    products = models.ManyToManyField(Products, blank=True, related_name="products", through="BookingProduct")
    services = models.ManyToManyField(Services, blank=True, related_name="services", through="BookingService")
    promotions = models.ManyToManyField(Promotion, blank=True, related_name="promotions", through="BookingPromotion")
    cancel_reason = models.TextField(null=True, blank=True, default=None)
    cancel_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    sent_notify = models.IntegerField(default=0)


class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, null=True, blank=True, on_delete=models.SET_NULL)
    staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL)
    service_name = models.CharField(null=True, blank=True, max_length=200)
    start_date = models.DateTimeField(null=True, blank=True, default=None)
    end_date = models.DateTimeField(null=True, blank=True, default=None)
    duration = models.IntegerField(null=True, blank=True, default=None)
    price = models.FloatField(null=True, blank=True, default=None)
    quantity = models.IntegerField(null=True, blank=True, default=None)
    note = models.TextField(null=True, blank=True, default=None)
    merchant_event = models.ForeignKey(
        "events.Event", related_name="merchant_events", null=True, blank=True, on_delete=models.SET_NULL
    )
    booked_user_event = models.ForeignKey(
        "events.Event", related_name="booked_user_events", null=True, blank=True, on_delete=models.SET_NULL
    )
    staff_event = models.ForeignKey(
        "events.Event", related_name="staff_events", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_anyone = models.BooleanField(default=False)
    service_info = JSONField(default=dict, null=True, blank=True)
    staff_info = JSONField(default=dict, null=True, blank=True)
    merchant_info = JSONField(default=dict, null=True, blank=True)


class BookingProduct(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(null=True, blank=True, default=None)
    price = models.FloatField(null=True, blank=True, default=None)
    product_info = JSONField(default=dict, null=True, blank=True)


class BookingPromotion(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, null=True, blank=True, on_delete=models.SET_NULL)
    price = models.FloatField(null=True, blank=True, default=0)
    unit = models.CharField(null=True, blank=True, max_length=100)
    promotion_info = JSONField(default=dict, null=True, blank=True)
