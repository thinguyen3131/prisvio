from django.db.models import Q
from rest_framework import generics

from prismvio.bookings.api.serializers import BookingSerializer, CancelBookingSerializer
from prismvio.bookings.constants import BOOKING_SORT_FIELDS
from prismvio.bookings.exceptions import BookingDoesNotExists
from prismvio.bookings.models import Booking, BookingService


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        merchant_id = self.request.GET.get("merchant_id", None)
        user_id = self.request.GET.get("user_id", None)
        updated_at = self.request.GET.get("updated_at", None)
        sort_by = self.request.GET.get("sort_by")
        order = self.request.GET.get("order", "asc")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        service_start_date = self.request.GET.get("service_start_date")
        service_end_date = self.request.GET.get("service_end_date")
        staff_id = self.request.GET.get("staff_id")
        where = Q()
        if merchant_id:
            where &= Q(merchant_id=merchant_id)
        if user_id:
            where &= Q(booked_user=user_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if start_date:
            where &= Q(start_date__gte=start_date)
        if end_date:
            where &= Q(end_date__lte=end_date)
        # TODO refactor this
        booking_service_where = Q()
        if staff_id:
            booking_service_where &= Q(staff__id=staff_id)
        if service_start_date:
            booking_service_where &= Q(start_date__gte=service_start_date)
        if service_end_date:
            booking_service_where &= Q(start_date__lte=service_end_date)
        if service_start_date or service_end_date:
            booking_ids = (
                BookingService.objects.filter(booking_service_where).values_list("booking_id", flat=True).distinct()
            )
            where &= Q(id__in=booking_ids)
        queryset = Booking.objects.filter(where)
        if sort_by and sort_by in BOOKING_SORT_FIELDS:
            order_by = sort_by
            if order == "desc":
                order_by = f"-{sort_by}"
            queryset = queryset.order_by(order_by)
        return queryset

    def perform_create(self, serializer):
        serializer.save(booked_user=self.request.user)


class BookingDetailAPIView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer

    def get_object(self):
        try:
            return Booking.objects.get(pk=self.kwargs.get("pk"))
        except Booking.DoesNotExist:
            raise BookingDoesNotExists()


class CancelBookingAPIView(generics.UpdateAPIView):
    serializer_class = CancelBookingSerializer

    def get_object(self):
        try:
            return Booking.objects.get(pk=self.kwargs.get("pk"))
        except Booking.DoesNotExist:
            raise BookingDoesNotExists()

    def perform_update(self, serializer):
        serializer.save(cancel_by=self.request.user)
