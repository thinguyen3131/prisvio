from django.urls import path

from booking.api.views import BookingDetailAPIView, BookingListCreateView, CancelBookingAPIView

urlpatterns = [
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingDetailAPIView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/cancel/', CancelBookingAPIView.as_view(), name='cancel-booking'),
]
