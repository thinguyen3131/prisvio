from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # call_command("makemigrations")
        # call_command("migrate")
        call_command("loaddata", "email_template.json")
        call_command("loaddata", "create_hashtag.json")
        call_command("loaddata", "create_keyword.json")
        call_command("loaddata", "create_category.json")
        call_command("loaddata", "create_country.json")
        call_command("loaddata", "create_province.json")
        call_command("loaddata", "create_district.json")
        call_command("loaddata", "create_ward.json")
        call_command("loaddata", "create_user.json")
        call_command("loaddata", "create_merchant.json")
        call_command("loaddata", "create_service.json")
        call_command("loaddata", "create_product.json")
        call_command("loaddata", "create_promotion.json")
