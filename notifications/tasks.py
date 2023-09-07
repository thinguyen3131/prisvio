import logging

from celery_logs.utils import CeleryDatabaseLogger
from prisvio.celery import app
from notifications.pushers import FireBasePusher

logger = logging.getLogger('django')


@app.task(bind=True, name="vio_push_notification")
def send_notification_task(self, data: dict):
    with CeleryDatabaseLogger(self):
        logger.info(f'{data} -- send push notification')
        FireBasePusher().send(message=data)
