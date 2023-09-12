from typing import List

from django.db import transaction

from prismvio.notifications.models import Message
from prismvio.notifications.tasks import send_notification_task


class PushManager:
    @classmethod
    def send_async_bulk(cls, messages: List[dict]):
        instances = []
        for message in messages:
            instances.append(Message(**message))
        Message.objects.bulk_create(instances)

        # Send messages
        for message in messages:
            message.pop('target_object', None)
            transaction.on_commit(lambda: send_notification_task.delay(data=message))
