from enum import Enum, unique

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmailTemplateLanguage(TextChoices):
    ENG = _("eng")
    VIE = _("vie")


@unique
class MailOutgoingStatus(str, Enum):
    NA = None
    SSL_TLS = "ssl/tls"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.NA.value, None),
            (cls.SSL_TLS.value, "SSL/TLS"),
        )
