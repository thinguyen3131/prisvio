import enum


@enum.unique
class GenderEnum(str, enum.Enum):
    MALE = 'Male'
    FEMALE = 'Female'

    @classmethod
    def choices(cls):
        return (
            (cls.MALE.value, 'Male'),
            (cls.FEMALE.value, 'Female'),
        )


@enum.unique
class LinkStatusEnum(str, enum.Enum):
    UNLINKED = 'Unlinked'
    LINKED = 'Linked'

    @classmethod
    def choices(cls):
        return (
            (cls.UNLINKED.value, 'Unlinked'),
            (cls.LINKED.value, 'Linked'),
        )


@enum.unique
class InviteStatusEnum(str, enum.Enum):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'

    @classmethod
    def choices(cls):
        return (
            (cls.PENDING.value, 'Pending'),
            (cls.ACCEPTED.value, 'Accepted'),
        )
