from config.celery_app import app
from prismvio.bookings.services.booking import create_booking_event, create_staff_booking_event


@app.task(bind=True, name="create_booking_event")
def create_booking_event_task(self, data: dict):
    create_booking_event(data)


@app.task(bind=True, name="create_staff_booking_event")
def create_staff_booking_event_task(self, staff_id: int, user_id: int):
    create_staff_booking_event(staff_id, user_id)
