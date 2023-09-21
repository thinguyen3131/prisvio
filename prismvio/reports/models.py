from django.conf import settings
from django.db import models


class ReportType(models.Model):
    name_vi = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)


class Report(models.Model):
    content = models.TextField(null=True, blank=True)
    report_type = models.ForeignKey(ReportType, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='reports',
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL,
                             help_text="Reporter")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    deleted_at = models.DateTimeField(default=None, null=True, blank=True)
