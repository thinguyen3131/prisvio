
import inspect
from contextlib import contextmanager
from time import time

from celery.states import FAILURE, SUCCESS

from celery_logs.models import CeleryTask


@contextmanager
def inner_func_log_exceptions(task, console_logger, _prefix: str = ''):
    try:
        yield
    except Exception as e:
        msg = str(e)
        meta = task.AsyncResult(task.request.id).info or {}
        meta.update({f'{_prefix}_error': msg})
        task.update_state(meta=meta)
        console_logger.error(f'{_prefix}_error -- {msg}')


class CeleryDatabaseLogger(object):
    """Init task in database, write state and execution time of celery task"""
    def __init__(self, task):
        self.task = task

    def __enter__(self):
        self.start_time = time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        str_exc_value = str(exc_value)
        db_task = CeleryTask(
            task_id=self.task.request.id, task_name=inspect.stack()[1].function,
            exec_time=round(time() - self.start_time, 2),
        )
        result = self.task.AsyncResult(self.task.request.id).info or {} if self.task.request.id else {}
        if isinstance(result, dict):
            meta = result
        else:
            meta = dict(task_result=result)
        meta.update({'args': self.task.request.args})
        if self.task.request.eta:
            meta.update({'eta': self.task.request.eta})
        if exc_type:
            db_task.status = FAILURE
            meta.update({'error': str_exc_value})
            db_task.meta = meta
            db_task.save()
            raise
        else:
            db_task.status = SUCCESS
            db_task.meta = meta
            db_task.save()

    def log(self, update_dict: dict) -> None:
        """Update logs to database ex: {"issue": "value"}"""
        meta = self.task.AsyncResult(self.task.request.id).info or {}
        meta.update(update_dict)
        self.task.update_state(meta=meta)
