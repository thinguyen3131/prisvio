from django.conf import settings
from django.db import models


class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="events", on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    images = models.JSONField(default=list, null=True, blank=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    event_data = models.JSONField(default=dict, null=True, blank=True)
    merchant_id = models.IntegerField(blank=True, null=True)
    staff_id = models.IntegerField(blank=True, null=True)
