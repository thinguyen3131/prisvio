from django.contrib import admin

# Register your models here.
from prismvio.merchant.models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    pass
