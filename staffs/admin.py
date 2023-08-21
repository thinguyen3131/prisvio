from django.contrib import admin

from staffs.models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('email', 'user')
    search_fields = ('email', 'user')
