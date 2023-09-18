from django.core.management import BaseCommand
from faker import Faker

from prismvio.menu_merchant.models import Hashtag, Keyword
from prismvio.merchant.models import Merchant


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker()
        hashtag, _ = Hashtag.objects.get_or_create(name='spa')
        keyword, _ = Keyword.objects.get_or_create(name='spa')

        for _ in range(50):
            merchant = Merchant.objects.create(
                name=f"{fake.company()} Spa",
                description=fake.paragraph(nb_sentences=3),
                latitude=40.58,
                longitude=40.58,
            )
            merchant.hashtags.add(hashtag)
            merchant.keywords.add(keyword)
            merchant.save()
