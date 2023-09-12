import json
from datetime import datetime, timezone

import pytz

# from events.models import Event
from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff
from prismvio.users.models import User
from prismvio.bookings.models import BookingService


def create_booking_event(data: dict) -> None:
    """Creates booking event

    Args:
        data: Booking data
    """
    pass
    # booking_id = data.get('id')
    # services = data.get('services')
    # merchant_id = data.get('merchant')
    # booked_user = User.objects.get(pk=data.get('booked_user'))
    # merchant = Merchant.objects.select_related("owner").get(pk=merchant_id)
    # for service in services:
    #     service_id = service.get('service_id')
    #     staff_id = service.get('staff')
    #     staff = Staff.objects.select_related("user").get(pk=staff_id)
    #     staff_user = staff.user
    #     event_start_datetime = datetime.fromisoformat(service.get('start_date')[:-1]).astimezone(timezone.utc)
    #     event_end_datetime = datetime.fromisoformat(service.get('end_date')[:-1]).astimezone(timezone.utc)
    #     user_event = Event.objects.create(
    #         event_start_datetime=event_start_datetime,
    #         start=event_start_datetime,
    #         event_end_datetime=event_end_datetime,
    #         end=event_end_datetime,
    #         start_timezone='UTC',
    #         end_timezone='UTC',
    #         event_data=json.dumps(data),
    #         merchant_id=merchant_id,
    #         user=booked_user,
    #     )
    #
    #     merchant_event = Event.objects.create(
    #         event_start_datetime=event_start_datetime,
    #         start=event_start_datetime,
    #         event_end_datetime=event_end_datetime,
    #         end=event_end_datetime,
    #         start_timezone='UTC',
    #         end_timezone='UTC',
    #         event_data=json.dumps(data),
    #         merchant_id=merchant_id,
    #         user=merchant.owner,
    #     )
    #     staff_event = None
    #     if staff_user:
    #         staff_event = Event.objects.create(
    #             event_start_datetime=event_start_datetime,
    #             start=event_start_datetime,
    #             event_end_datetime=event_end_datetime,
    #             end=event_end_datetime,
    #             start_timezone='UTC',
    #             end_timezone='UTC',
    #             event_data=json.dumps(data),
    #             merchant_id=merchant_id,
    #             user=staff_user,
    #             staff_id=staff_id,
    #         )
    #
    #     BookingService.objects.filter(
    #         service=service_id,
    #         booking=booking_id).update(
    #         merchant_event=merchant_event,
    #         booked_user_event=user_event,
    #         staff_event=staff_event,
    #     )


def create_staff_booking_event(staff_id: int, user_id: int):
    pass
    # services = BookingService.objects.select_related('staff', 'merchant_event').filter(
    #     staff_id=staff_id,
    #     staff_event__isnull=True,
    #     start_date__lte=datetime.now(tz=pytz.UTC),
    # )
    # for service in services:
    #     staff_event = Event.objects.create(
    #         event_start_datetime=service.merchant_event.event_start_datetime,
    #         start=service.merchant_event.start,
    #         event_end_datetime=service.merchant_event.event_end_datetime,
    #         end=service.merchant_event.end,
    #         start_timezone='UTC',
    #         end_timezone='UTC',
    #         event_data=service.merchant_event.event_data,
    #         merchant_id=service.merchant_event.merchant_id,
    #         user_id=user_id,
    #         staff_id=staff_id,
    #     )
    #     service.staff_event = staff_event
    #     service.save()
