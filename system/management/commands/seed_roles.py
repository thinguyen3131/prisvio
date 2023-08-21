from django.core.management.base import BaseCommand, CommandError

from slugify import slugify

from core.utils.enums import (AppointmentRole, AthleticClubProfileRole, ConversationRole, DoctorProfileRole,
                              GymProfileRole, ResourceType, ShopProfileRole, UniversityProfileRole)
from system.models import Resource, Role


def seed_roles(resource_type_value, role_enum):
    resource_slug = slugify(resource_type_value.name.lower(), separator='_')
    try:
        resource = Resource.objects.get(slug=resource_slug)
    except Resource.DoesNotExist:
        raise CommandError(f'The resource {resource_slug} does not exist.')

    for role in list(role_enum):
        slug = slugify(role.name.lower(), separator='_')
        try:
            Role.objects.get(slug=slug, resource=resource)
        except Role.DoesNotExist:
            Role.objects.create(
                name=f'{resource_type_value.value} - {role.value} Role',
                slug=slug,
                label=role.value,
                resource=resource,
                editable=False,
            )


class Command(BaseCommand):
    help = 'Seed data for the roles'

    def handle(self, *args, **options):
        seed_roles(ResourceType.CONVERSATION, ConversationRole)
        seed_roles(ResourceType.UNIVERSITY_PROFILE, UniversityProfileRole)
        seed_roles(ResourceType.DOCTOR_PROFILE, DoctorProfileRole)
        seed_roles(ResourceType.ATHLETIC_CLUB_PROFILE, AthleticClubProfileRole)
        seed_roles(ResourceType.GYM_PROFILE, GymProfileRole)
        seed_roles(ResourceType.SHOP_PROFILE, ShopProfileRole)
        seed_roles(ResourceType.APPOINTMENT, AppointmentRole)
