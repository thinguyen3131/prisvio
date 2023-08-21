from django.core.management.base import BaseCommand

from slugify import slugify

from core.utils.enums import ResourceType
from system.models import Resource


class Command(BaseCommand):
    help = 'Seed data for the resources'

    def handle(self, *args, **options):
        for resource in list(ResourceType):
            slug = slugify(resource.name.lower(), separator='_')
            try:
                Resource.objects.get(slug=slug)
            except Resource.DoesNotExist:
                Resource.objects.create(
                    name=resource.value,
                    slug=slug,
                    editable=False,
                )
