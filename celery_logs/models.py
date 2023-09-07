
from django.db.models import JSONField
from django.db import models

from celery.states import PENDING

from celery_logs.managers import CeleryTaskObjectManager


class CeleryTask(models.Model):
    """Tracking heavy tasks"""
    # max number of stored tasks logs in database
    MAX_NUM_ROWS = 5000

    task_id = models.CharField(max_length=50, verbose_name='Celery task id', null=True)
    exec_time = models.FloatField(max_length=50, null=True, verbose_name='Execution_time')
    task_name = models.CharField(null=True, max_length=255, db_index=True, verbose_name='Task Name',
                                 help_text='Name of the Task which was run')
    status = models.CharField(max_length=20, default=PENDING, db_index=True, verbose_name='Task State',
                              help_text='Current state of the task being run')
    date_update = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Last updated DateTime',
                                       help_text='Datetime field when the task was updated in UTC')
    traceback = models.TextField(blank=True, null=True, verbose_name='Traceback',
                                 help_text='Text of the traceback if the task generated one')
    meta = JSONField(null=True, default=None, editable=False, verbose_name='Task Meta Information',
                     help_text='JSON meta information about the task, such as information on child tasks')

    objects = CeleryTaskObjectManager()

    def __str__(self):
        return f'{self.task_id} {self.task_name}'
