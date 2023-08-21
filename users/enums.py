from enum import Enum, IntEnum, unique


@unique
class UserReminderResource(str, Enum):
    EVENT = 'event'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.EVENT.value, 'Event'),
        )


@unique
class NotificationSettingResource(str, Enum):
    PROFILE = 'profile'
    EVENT = 'event'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.PROFILE.value, 'Profile'),
            (cls.EVENT.value, 'Event'),
        )


@unique
class OTPType(str, Enum):
    PHONE_NUMBER = 'phone'
    EMAIL = 'email'


@unique
class OTPAction(str, Enum):
    ID_VERIFICATION = 'ID_VERIFICATION'
    PASSWORD_RESET = 'PASSWORD_RESET'


class IntervalLockTime(IntEnum):
    SEND = 60 * 5  # 5 minutes
    CHECK = 60 * 5  # 5 minutes


class MaxTime(IntEnum):
    SEND = 3  # Can send 3 times before be locked
    CHECK = 5  # Can check 5 times before be locked


@unique
class UserTypeOption(str, Enum):
    BUSINESS = 3
    PERSONAL = 1

    @classmethod
    def choices(cls):
        return (
            (cls.BUSINESS.value, 3),
            (cls.PERSONAL.value, 1),
        )


@unique
class UserSettingKey(str, Enum):
    LANGUAGE = 'language'
    ALLOW_NOTIFICATIONS = 'allow_notifications'

    @classmethod
    def choices(cls):
        return (
            (cls.LANGUAGE.value, 'Language'),
            (cls.ALLOW_NOTIFICATIONS.value, 'Allow notifications'),
        )


@unique
class UserSettingDataType(str, Enum):
    BOOL = 'bool'
    INT = 'int'
    ARRAY = 'array'
    STRING = 'string'


@unique
class UserSettingLanguages(str, Enum):
    ENG = 'eng'
    VIE = 'vie'


@unique
class Currency(str, Enum):
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


class ReviewRating(IntEnum):
    ONE_STAR = 1
    TWO_STARS = 2
    THREE_STARS = 3
    FOUR_STARS = 4
    FIVE_STARS = 5

    @classmethod
    def choices(cls):
        return [(rating.value, rating.name) for rating in cls]
