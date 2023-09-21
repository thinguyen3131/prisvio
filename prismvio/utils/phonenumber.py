import phonenumbers
from django.utils.translation import gettext_lazy as _
from phonenumbers import region_code_for_country_code
from rest_framework.exceptions import ValidationError


def validate_phone_number(value: str, country_code=None):
    msg = _("Invalid phone number format.")
    try:
        phone = phonenumbers.parse(value, country_code)
        if not phone.country_code:
            raise ValidationError(msg)
        if not country_code:
            country_code = region_code_for_country_code(phone.country_code)
    except Exception:
        raise ValidationError(msg)
    if country_code and not phonenumbers.is_valid_number_for_region(phone, country_code):
        raise ValidationError(msg)
    value = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)

    return value


def get_country_code_from_phone_number(value: str):
    msg = _("Invalid phone number format.")
    try:
        phone = phonenumbers.parse(value)
    except Exception:
        raise ValidationError(msg)

    return region_code_for_country_code(phone.country_code)
