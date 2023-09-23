import enum


@enum.unique
class PaymentMethodEnum(str, enum.Enum):
    CASH = "Cash"
    MOMO = "Momo"
    ZALO_PAy = "Zalo Pay"
    BANK_TRANSFER = "Bank_Transfer"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.CASH.value, "Cash"),
            (cls.MOMO.value, "Momo"),
            (cls.ZALO_PAy.value, "Zalo Pay"),
            (cls.BANK_TRANSFER.value, "Bank Transfer"),
        )


@enum.unique
class BookingStatusEnum(str, enum.Enum):
    UPCOMING = "Upcoming"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.UPCOMING.value, "Upcoming"),
            (cls.ONGOING.value, "Ongoing"),
            (cls.COMPLETED.value, "Completed"),
            (cls.CANCELED.value, "Canceled"),
        )
