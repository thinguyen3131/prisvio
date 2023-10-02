from django.contrib import admin

from prismvio.reports.models import Report, ReportType


@admin.register(ReportType)
class ReportTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name_vi", "name_en"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ["id", "content", "Category", "report_type"]
