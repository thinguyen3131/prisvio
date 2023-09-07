
from django.apps import AppConfig


class AsyncCeleryConfig(AppConfig):
    name = 'celery_logs'

    def ready(self):
        """Mount signals"""
        import celery_logs.signals  # noqa: F401
