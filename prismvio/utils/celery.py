from errno import errorcode

from django import conf
from django.db import transaction
from django.utils.module_loading import import_string
from loguru import logger

from config.celery_app import app as celery_app
from config.celery_app import run_task


class FailedCancellationException(Exception):
    pass


def add_task(fn, *args, **kwargs):
    if not isinstance(fn, str):
        fn = f"{fn.__module__}.{fn.__name__}"
    on_transaction_commit: bool = kwargs.pop("on_transaction_commit", False)
    logger.info(f"Adding task: {fn}")
    if conf.settings.TESTING:
        fn = import_string(fn)
        return fn(*args, **kwargs)
    if on_transaction_commit:
        return transaction.on_commit(lambda: run_task.delay(fn, *args, **kwargs))
    return run_task.delay(fn, *args, **kwargs)


def get_celery_worker_status():
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if not stats:
            stats = dict(error="No running Celery workers were found.")
    except OSError as error:
        message = f"Error connecting to the backend: {str(error)}"
        if len(error.args) > 0 and errorcode.get(error.args[0]) == "ECONNREFUSED":
            message += " Check that the RabbitMQ server is running."
        stats = dict(error=message)

    return stats


def cancel_task(task_id: str):
    try:
        stats = get_celery_worker_status()
        if "error" in stats:
            error_msg = stats["einfo"]
            logger.info(error_msg)
            raise FailedCancellationException(error_msg)
        else:
            celery_app.control.revoke(task_id)
    except Exception as error:
        logger.exception(error)
        raise FailedCancellationException("Can not cancel this task.")
