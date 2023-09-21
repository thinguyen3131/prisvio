import glob
import json
import os

from django.core.management import BaseCommand
from loguru import logger
from slugify import slugify

from config import settings
from prismvio.location.models import Country, District, Province, Ward
from prismvio.menu_merchant.models import Hashtag
from prismvio.merchant.models import Merchant


class Command(BaseCommand):
    def handle(self, *args, **options):
        directory_path = "fixtures/merchants"
        settings.ELASTICSEARCH_DSL_AUTOSYNC = False
        json_files = glob.glob(os.path.join(directory_path, "*.json"))

        for json_file in json_files:
            with open(json_file) as file:
                items = json.load(file)
                for data in items:
                    try:
                        country, _ = Country.objects.get_or_create(full_name_vi="Việt Nam")
                        province, _ = Province.objects.get_or_create(
                            name_vi=data["city"],
                            country=country,
                        )
                        district, _ = District.objects.get_or_create(
                            name_vi=data["district"],
                            country=country,
                            province=province,
                        )
                        ward, _ = Ward.objects.get_or_create(
                            name_vi=data["ward"],
                            country=country,
                            district=district,
                        )
                        merchant, _ = Merchant.objects.get_or_create(
                            name=data["name"],
                            country=country,
                            province=province,
                            district=district,
                            ward=ward,
                            defaults=dict(
                                latitude=data["latitude"],
                                longitude=data["longitude"],
                                address=data["address"],
                            ),
                        )
                        for cat in data["categories"]:
                            cat_name = cat["name"]
                            tag_name = slugify(cat_name.strip(), word_boundary=True, separator=" ", lowercase=True)
                            hashtag, _ = Hashtag.objects.get_or_create(name=tag_name)
                            merchant.hashtags.add(hashtag)
                        merchant.save()
                    except Exception as err:
                        logger.error(str(err))
                        continue
