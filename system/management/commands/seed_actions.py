from django.core.management import BaseCommand, CommandError

from slugify import slugify

from core.utils.enums import (AthleticClubProfileAction, DoctorProfileAction, GymProfileAction, ResourceType,
                              ShopProfileAction, UniversityProfileAction)
from system.models import Action, Resource


def seed_actions(resource_type_value, action_enum):
    resource_slug = slugify(resource_type_value.name.lower(), separator='_')
    try:
        resource = Resource.objects.get(slug=resource_slug)
    except Resource.DoesNotExist:
        raise CommandError(f'The resource {resource_slug} does not exist.')

    for action in list(action_enum):
        slug = slugify(action.name.lower(), separator='_')
        try:
            Action.objects.get(slug=slug, resource=resource)
        except Action.DoesNotExist:
            Action.objects.create(
                name=f'{resource_type_value.value} - {action.value}',
                slug=slug,
                resource=resource,
            )


class Command(BaseCommand):
    help = 'Seed data for the resource actions'

    def handle(self, *args, **options):
        seed_actions(ResourceType.UNIVERSITY_PROFILE, UniversityProfileAction)
        seed_actions(ResourceType.DOCTOR_PROFILE, DoctorProfileAction)
        seed_actions(ResourceType.GYM_PROFILE, GymProfileAction)
        seed_actions(ResourceType.SHOP_PROFILE, ShopProfileAction)
        seed_actions(ResourceType.ATHLETIC_CLUB_PROFILE, AthleticClubProfileAction)
