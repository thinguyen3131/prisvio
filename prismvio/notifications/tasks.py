import logging

from config.celery_app import app
from prismvio.notifications.pushers import FireBasePusher

logger = logging.getLogger("django")


@app.task(bind=True, name="vio_push_notification")
def send_notification_task(self, data: dict):
    logger.info(f"{data} -- send push notification")
    FireBasePusher().send(message=data)
