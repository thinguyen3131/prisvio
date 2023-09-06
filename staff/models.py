from django.conf import settings
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from staff.enums import GenderEnum, InviteStatusEnum, LinkStatusEnum


class Staff(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True)
    avatar = models.JSONField(default=dict, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=50, blank=True, null=True, choices=GenderEnum.choices())
    invite_status = models.CharField(max_length=50, null=True, blank=True,
                                     choices=InviteStatusEnum.choices(),
                                     default=None)
    link_status = models.CharField(max_length=50, null=True, blank=True,
                                   choices=LinkStatusEnum.choices(),
                                   default=LinkStatusEnum.UNLINKED.value)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    merchant = models.ForeignKey('merchant.Merchant',
                                 related_name='staff',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    price = models.FloatField(null=True, blank=True)
    country_code = models.CharField(max_length=4, null=True, blank=True)
    country_number = models.CharField(max_length=4, null=True, blank=True)
    platform_number = models.CharField(max_length=45, null=True, blank=True)
    is_show = models.BooleanField(default=True)  # show staff in specific service
    is_require_service = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # the staff off in a specific time.
    total_bookings = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name