from copy import deepcopy

from django.db.models import Q
from rest_framework import generics

from prismvio.bookings.api.serializers import BookingSerializer, CancelBookingSerializer
from prismvio.bookings.exceptions import BookingDoesNotExists
from prismvio.bookings.models import Booking
from prismvio.utils.drf_utils import search


class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        query_params = deepcopy(self.request.query_params)
        staff_ids = query_params.getlist("staff_ids", None)
        merchant_id = query_params.get("merchant_id", None)
        user_id = query_params.get("user_id", None)
        updated_at = query_params.get("updated_at", None)
        start_date = query_params.get("start_date")
        end_date = query_params.get("end_date")
        service_start_date = query_params.get("service_start_date")
        service_end_date = query_params.get("service_end_date")
        where = Q()
        if merchant_id:
            where |= Q(merchant_id=merchant_id)
        if user_id:
            where |= Q(booked_user=user_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        if start_date:
            where &= Q(start_date__gte=start_date)
        if end_date:
            where &= Q(end_date__lte=end_date)
        if staff_ids:
            where &= Q(bookingservice__staff__id__in=staff_ids)
        if service_start_date:
            where &= Q(bookingservice__start_date__gte=service_start_date)
        if service_end_date:
            where &= Q(bookingservice__start_date__lte=service_end_date)
        queryset = Booking.objects.filter(where)
        exclude_fields = ["updated_at", "start_date", "end_date", "service_end_date", "service_start_date"]
        return search(queryset=queryset, query_params=query_params, model=Booking, exclude_fields=exclude_fields)

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
