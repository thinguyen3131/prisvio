
from django.contrib import admin

from celery_logs.models import CeleryTask


@admin.register(CeleryTask)
class CeleryTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_name', 'meta', 'exec_time', 'date_update', 'status')
