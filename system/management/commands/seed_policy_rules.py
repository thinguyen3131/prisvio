from django.core.management.base import BaseCommand

from core.utils.command import seed_data
from system.models import PolicyRule


class Command(BaseCommand):
    help = 'Seed data for the policy rule'

    def handle(self, *args, **options):
        seed_data('fixtures/4_policy_rules.json', PolicyRule, key_fields=['v1'],
                  update=True, updated_fields=['v0', 'v2'])
