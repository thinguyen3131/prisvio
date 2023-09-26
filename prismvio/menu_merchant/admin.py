from django.contrib import admin

# Register your models here.
from prismvio.menu_merchant.models import Category, Hashtag, Product, Promotion, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    pass


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    pass


@admin.register(Service)
class ServicesAdmin(admin.ModelAdmin):
    pass
