import uuid

import shortuuid
from django.conf import settings
from django.db import models
from slugify import slugify
from timezone_field import TimeZoneField

from prismvio.location.models import Country, District, Province, Ward
from prismvio.merchant.enums import MerchantCurrency


class MerchantManager(models.Manager):
    def get_with_related_data(self):
        return self.prefetch_related(
            "hashtags",
            "keywords",
        ).select_related(
            "country",
            "province",
            "district",
            "ward",
        )


class Merchant(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="merchants", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(default=None, max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True)
    country_code = models.CharField(max_length=4, null=True, blank=True)
    country_number = models.CharField(max_length=4, null=True, blank=True)
    platform_number = models.CharField(max_length=45, null=True, blank=True)
    website = models.CharField(null=True, blank=True, max_length=255)
    timezone = TimeZoneField(default="Asia/Ho_Chi_Minh", null=True, blank=True)
    currency = models.CharField(
        max_length=20, choices=MerchantCurrency.choices, default=MerchantCurrency.VND.value, blank=True, null=True
    )
    uid = models.CharField(max_length=64, null=True, blank=True, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    hashtags = models.ManyToManyField("menu_merchant.Hashtag", blank=True, related_name="merchants")
    categories = models.ManyToManyField("menu_merchant.Category", blank=True, related_name="merchants")
    keywords = models.ManyToManyField("menu_merchant.Keyword", blank=True, related_name="merchants")
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="connect with country in table country location",
    )
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="connect with Province in table Province location",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="connect with District in table District location",
    )
    ward = models.ForeignKey(
        Ward, on_delete=models.CASCADE, null=True, blank=True, help_text="connect with Ward in table Ward location"
    )
    is_staffs_visible = models.BooleanField(default=True)
    total_available_slot = models.IntegerField(default=0, null=True, blank=True)
    total_available_slots_unit = models.CharField(max_length=45, null=True, blank=True)
    total_bookings = models.IntegerField(default=0, null=True, blank=True)
    opening_date = models.DateTimeField(null=True, blank=True)
    avatar = models.JSONField(default=dict, null=True, blank=True, help_text="Avatar of merchant vio app")
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    objects = MerchantManager()

    def __str__(self):
        if self.name:
            return self.name
        return f"Merchant ID=[{self.id}]"

    def save(self, *args, **kwargs):
        if not self.uid:
            unique_id = uuid.uuid4()
            self.uid = shortuuid.encode(unique_id)

        super().save(*args, **kwargs)

    def normalizer_name(self):
        if self.name:
            normalizer = slugify(self.name.strip(), word_boundary=True, separator=" ", lowercase=True)
            return normalizer
        return None

    def position(self):
        if self.latitude and self.longitude:
            return {
                "lat": float(self.latitude),
                "lon": float(self.longitude),
            }
        return None


class TimeslotCollectionMerchant(models.Model):
    merchant = models.ForeignKey(
        "merchant.Merchant", related_name="timeslotcollection", on_delete=models.CASCADE, null=True, blank=True
    )
    weekly = models.JSONField(default=list, null=True, blank=True)
    daily = models.JSONField(default=list, null=True, blank=True)
    shifts = models.JSONField(default=list, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class ExclusionDate(models.Model):
    merchant = models.ForeignKey(
        "merchant.Merchant", related_name="exclusion_date", on_delete=models.CASCADE, null=True, blank=True
    )
    note = models.CharField(max_length=255, blank=True, null=True)
    dates = models.JSONField(default=list, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
