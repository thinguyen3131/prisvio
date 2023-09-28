import json
from datetime import datetime, timezone

import pytz

from prismvio.bookings.models import BookingService
from prismvio.events.models import Event
from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff
from prismvio.users.models import User


def create_booking_event(data: dict) -> None:
    """Creates booking event

    Args:
        data: Booking data
    """
    booking_id = data.get("id")
    services = data.get("services")
    merchant_id = data.get("merchant")
    booked_user = User.objects.get(pk=data.get("booked_user"))
    merchant = Merchant.objects.select_related("owner").get(pk=merchant_id)
    for service in services:
        service_id = service.get("service_id")
        staff_id = service.get("staff")
        staff = Staff.objects.select_related("user").get(pk=staff_id)
        staff_user = staff.user
        start_date = datetime.fromisoformat(service.get("start_date")[:-1]).astimezone(timezone.utc)
        end_date = datetime.fromisoformat(service.get("end_date")[:-1]).astimezone(timezone.utc)
        user_event = Event.objects.create(
            start_date=start_date,
            end_date=end_date,
            event_data=json.dumps(data),
            merchant_id=merchant_id,
            user=booked_user,
        )

        merchant_event = Event.objects.create(
            start_date=start_date,
            end_date=end_date,
            event_data=json.dumps(data),
            merchant_id=merchant_id,
            user=merchant.owner,
        )
        staff_event = None
        if staff_user:
            staff_event = Event.objects.create(
                start_date=start_date,
                end_date=end_date,
                event_data=json.dumps(data),
                merchant_id=merchant_id,
                user=staff_user,
                staff_id=staff_id,
            )

        BookingService.objects.filter(service=service_id, booking=booking_id).update(
            merchant_event=merchant_event,
            booked_user_event=user_event,
            staff_event=staff_event,
        )


def create_staff_booking_event(staff_id: int, user_id: int):
    services = BookingService.objects.select_related("staff", "merchant_event").filter(
        staff_id=staff_id,
        staff_event__isnull=True,
        start_date__lte=datetime.now(tz=pytz.UTC),
    )
    for service in services:
        staff_event = Event.objects.create(
            start_date=service.merchant_event.start_date,
            end_date=service.merchant_event.end_date,
            event_data=service.merchant_event.event_data,
            merchant_id=service.merchant_event.merchant_id,
            user_id=user_id,
            staff_id=staff_id,
        )
        service.staff_event = staff_event
        service.save()
