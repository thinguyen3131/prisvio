from prisvio.celery import app
# TODO waiting event module
# from booking.services.booking import create_booking_event, create_staff_booking_event


@app.task(bind=True, name="create_booking_event")
def create_booking_event_task(self, data: dict):
    # TODO waiting event module
    # create_booking_event(data)
    pass


@app.task(bind=True, name="create_staff_booking_event")
def create_staff_booking_event_task(self, staff_id: int, user_id: int):
    # TODO waiting event module
    # create_staff_booking_event(staff_id, user_id)
    pass
