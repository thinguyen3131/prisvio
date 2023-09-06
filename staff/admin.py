from django.contrib import admin

from staff.models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('email', 'user')
    search_fields = ('email', 'user')
