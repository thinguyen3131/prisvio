from django.core.management.base import BaseCommand

from prismvio.system.models import EmailTemplate
from prismvio.utils.command import seed_data


class Command(BaseCommand):
    help = "Seed data for email template"

    def handle(self, *args, **options):
        try:
            seed_data("fixtures/2_email_template.json", EmailTemplate, key_fields=["name"])
        except Exception as e:
            print(str(e))
        pass
