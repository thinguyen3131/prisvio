from django.core.management.base import BaseCommand

from core.utils.command import seed_data
from users.models import UserReportType


class Command(BaseCommand):
    help = 'Seed data for report type'

    def handle(self, *args, **options):
        try:
            seed_data('fixtures/5_report_type.json', UserReportType, key_fields=['name'])
        except Exception as e:
            print(str(e))
        pass
