from django.core.management.base import BaseCommand

from core.utils.command import seed_data
from system.models import EmailTemplate


class Command(BaseCommand):
    help = 'Seed data for email template'

    def handle(self, *args, **options):
        try:
            seed_data('fixtures/2_email_template.json', EmailTemplate, key_fields=['name'])
        except Exception as e:
            print(str(e))
        pass
