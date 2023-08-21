from django.core.management.base import BaseCommand

# from core.utils.command import seed_data
# from system.models import SMSTemplate


class Command(BaseCommand):
    help = 'Seed data for sms template'

    def handle(self, *args, **options):
        # try:
        #     seed_data('fixtures/sms_template.json', SMSTemplate, key_field='name')
        # except Exception as e:
        #     print(str(e))
        pass
