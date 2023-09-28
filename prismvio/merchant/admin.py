from django.contrib import admin

# Register your models here.
from prismvio.merchant.models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone_number", "address", "is_active"]
    # list_filter = ['user']
    search_fields = ["name", "email", "phone_number", "address", "is_active"]
    list_per_page = 20
