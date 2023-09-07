from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmailTemplateLanguage(TextChoices):
    ENG = _("eng")
    VIE = _("vie")
