from django.db.models import TextChoices


class MerchantCurrency(TextChoices):
    VND = "VND"
    USD = "USD"
    EUR = "EUR"
