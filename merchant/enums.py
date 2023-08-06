import enum


@enum.unique
class MerchantCurrency(str, enum.Enum):
    VND = 'VND'
    USD = 'USD'
    EUR = 'EUR'

    @classmethod
    def choices(cls):
        return (
            (cls.VND.value, 'VND'),
            (cls.USD.value, 'USD'),
            (cls.EUR.value, 'EUR'),
        )
