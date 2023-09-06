from enum import Enum, IntEnum, unique


@unique
class OTPType(str, Enum):
    PHONE_NUMBER = "phone"
    EMAIL = "email"


@unique
class OTPAction(str, Enum):
    ID_VERIFICATION = "ID_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"


class IntervalLockTime(IntEnum):
    SEND = 60 * 5  # 5 minutes
    CHECK = 60 * 5  # 5 minutes


class MaxTime(IntEnum):
    SEND = 3  # Can send 3 times before be locked
    CHECK = 5  # Can check 5 times before be locked
