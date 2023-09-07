import logging
import os
import sys

from celery import Celery
from celery.signals import setup_logging
from django.conf import settings
from django.utils.module_loading import import_string
from loguru import logger

from config.logging import InterceptHandler

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("prismvio")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    broker_connection_retry_on_startup=True,
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


if settings.DEBUG:

    @setup_logging.connect
    def setup_logging(loglevel: int = logging.WARN, **_):
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "level": loglevel,
                    "format": settings.LOGURU_FORMAT,
                }
            ],
        )
        handler = InterceptHandler(level=loglevel)
        log = logging.getLogger("celery")
        log.propagate = False
        log.addHandler(handler)
        log.setLevel(loglevel)
        return log


@app.task(bind=True)
def run_task(self, *args, **kwargs):
    fn = import_string(args[0])
    args = args[1:] if len(args) > 1 else ()

    return fn(*args, **kwargs)
