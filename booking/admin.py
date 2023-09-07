from django.contrib import admin

# Register your models here.
from booking.models import Booking, BookingService


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass


@admin.register(BookingService)
class BookingServiceAdmin(admin.ModelAdmin):
    pass
