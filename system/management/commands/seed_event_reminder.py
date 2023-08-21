import uuid

from django.core.management.base import BaseCommand
from django.db.models.functions import Length
from django.utils import timezone

from loguru import logger

from core.celery import FailedCancellationException, cancel_task
from system.enum import ScheduleStatus
from system.models import Schedule


class Command(BaseCommand):
    help = 'Seed event reminders'

    def handle(self, *args, **options):
        schedules = Schedule.objects.annotate(
            task_id_len=Length('task_id'),
        ).filter(
            period_of_time__lte=timezone.now(),
            app='events',
            worker='send_event_reminder',
            status=ScheduleStatus.RECEIVED.value,
            task_id_len=36,  # uuid
            task_id__isnull=False,
        )

        for instance in schedules:
            try:
                if not instance.task_id:
                    continue
                uuid.UUID(instance.task_id)
                cancel_task(instance.task_id)
            except ValueError:
                logger.info(f'Invalid task id: {instance.task_id}')
                continue
            except FailedCancellationException:
                pass
            except Exception as err:
                logger.info(f'Something wrong with task id: {instance.task_id}. Error: {err}')
                continue

            Schedule.objects.apply_schedule(instance)
