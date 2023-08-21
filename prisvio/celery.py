from __future__ import absolute_import, unicode_literals
import logging
import os
import sys
from decouple import config
from django.apps import apps
from django.utils.module_loading import import_string

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prisvio.settings')

app = Celery('prisvio', broker='redis://127.0.0.1:6379')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

