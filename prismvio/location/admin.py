from django.contrib import admin

from prismvio.location.models import Country, District, Province, Ward


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["code", "full_name_vi", "full_name_en"]
    search_fields = ["code", "full_name_vi", "full_name_en"]
    list_per_page = 20


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ["code", "name_vi", "name_en", "country"]
    search_fields = ["code", "name_vi", "name_en", "country"]
    list_per_page = 20


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ["code", "name_vi", "name_en", "province"]
    search_fields = ["code", "name_vi", "name_en", "province"]
    list_per_page = 20


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ["code", "name_vi", "name_en", "district"]
    search_fields = ["code", "name_vi", "name_en", "district"]
    list_per_page = 20
