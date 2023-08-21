from django.core.management.base import BaseCommand

from core.utils.command import seed_data
from system.models import SystemConfig


class Command(BaseCommand):
    help = 'Seed data for system config'

    def handle(self, *args, **options):
        try:
            seed_data('fixtures/8_system_config.json', SystemConfig, key_fields=['folder', 'name'])
        except Exception as e:
            print(str(e))
        pass
