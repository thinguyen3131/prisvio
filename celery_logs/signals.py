"""Signals"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from celery_logs.models import CeleryTask


@receiver(post_save, sender=CeleryTask)
def post_save_celery_db_log_handler(sender, **kwargs) -> None:
    """Post save signal for dropping extra celery db logs by MAX_NUM_ROWS and fast counter
    *Could be refactored with cache system in future
    """
    if kwargs.get('created', None):
        if CeleryTask.objects.count_estimate() > CeleryTask.MAX_NUM_ROWS:
            CeleryTask.objects.first().delete()
