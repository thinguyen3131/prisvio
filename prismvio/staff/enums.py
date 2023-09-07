from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class GenderEnum(TextChoices):
    MALE = _("Male")
    FEMALE = _("Female")


class LinkStatusEnum(TextChoices):
    UNLINKED = _("Unlinked")
    LINKED = _("Linked")


class InviteStatusEnum(TextChoices):
    PENDING = _("Pending")
    ACCEPTED = _("Accepted")
