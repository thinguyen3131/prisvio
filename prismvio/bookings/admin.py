from django.contrib import admin

# Register your models here.
from prismvio.bookings.models import Booking, BookingProduct, BookingPromotion, BookingService


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "merchant",
        "booked_user",
        "total_price",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "deleted_at",
    ]


@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(BookingProduct)
class BookingProductAdmin(admin.ModelAdmin):
    pass


@admin.register(BookingPromotion)
class BookingPromotionAdmin(admin.ModelAdmin):
    pass
