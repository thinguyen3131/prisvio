from django.urls import path

from prismvio.bookings.api.views import BookingDetailAPIView, BookingListCreateView, CancelBookingAPIView

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list-create"),
    path("<int:pk>/", BookingDetailAPIView.as_view(), name="booking-detail"),
    path("<int:pk>/cancel/", CancelBookingAPIView.as_view(), name="cancel-booking"),
]
