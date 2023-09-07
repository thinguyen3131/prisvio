import logging
from typing import List, Optional

from users.models import User
from notifications.services.manager import PushManager
from notifications.services.message import NotificationMessage

logger = logging.getLogger('django')


class BookingPushMessage(NotificationMessage):
    def __init__(self, user, booking):
        self.__user = user
        self.__booking = booking

    @property
    def user_id(self):
        return self.__user.pk

    @property
    def verb(self) -> str:
        return "booking"

    @property
    def title(self) -> str:
        return "booking"

    @property
    def content(self) -> str:
        return "hello"

    @property
    def target_object(self):
        return self.__booking

    @property
    def payload(self) -> Optional[dict]:
        """
        Extra payload for FCM
        :return:
        """
        return {
            'type': 'booking',
            'id': self.__booking.pk,
        }


class PushBookingMessage:
    def __init__(self, booking):
        self.booking = booking

    def send(self, user_ids: List[int]):
        try:
            messages = []
            users = User.objects.filter(pk__in=user_ids)
            for user in users.iterator():
                message = BookingPushMessage(user=user, booking=self.booking).dict()
                messages.append(message)
            self.booking.sent_notify += 1
            self.booking.save()

            PushManager.send_async_bulk(messages=messages)
            self.booking.save()
        except Exception as ex:
            logger.exception(ex)
