from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from sonyflake import SonyFlake
from timezone_field import TimeZoneField
from merchant.enums import MerchantCurrency


class Merchant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='merchants',
                              null=True,
                              blank=True,
                              on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(default=None, max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True)
    website = models.CharField(null=True, blank=True, max_length=255)
    timezone = TimeZoneField(default='Asia/Ho_Chi_Minh')
    currency = models.CharField(
        max_length=20,
        choices=MerchantCurrency.choices(),
        default=MerchantCurrency.VND.value,
    )
    uid = models.CharField(max_length=64, null=True, blank=True, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        return f'Merchant ID=[{self.id}]'

    # def save(self, *args, **kwargs):
    #     if not self.name:
    #         self.name = getattr(self.owner, 'brand_name', settings.MERCHANT_DEFAULT_NAME)

    #     if not self.uid:
    #         sf = SonyFlake(machine_id=get_machine_id)
    #         self.uid = str(sf.next_id())

    #     super().save(*args, **kwargs)


class TimeslotCollectionMerchant(models.Model):
    merchant = models.ForeignKey(Merchant,
                                 related_name='timeslotcollection',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    weekly = models.JSONField(default=list, null=True, blank=True)
    daily = models.JSONField(default=list, null=True, blank=True)
    shifts = models.JSONField(default=list, null=True, blank=True)

    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExclusionDate(models.Model):
    merchant = models.ForeignKey(Merchant,
                                 related_name='exclusion_date',
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    dates = models.DateField(default=list, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)