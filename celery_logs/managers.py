
from django.db import models

from prisvio.utils.db_utils import approximate_row_count


class CeleryTaskObjectManager(models.Manager):
    """Celery tasks database manager for implementing quick count function"""

    def count_estimate(self) -> int:
        """Quick but inaccurate count of celery tasks in database"""
        return approximate_row_count(self.model._meta.db_table)
