import enum


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return enum.Enum(added_enum.__name__, joined)
    return wrapper


class ResourceType(str, enum.Enum):
    CONVERSATION = 'Conversation'
    UNIVERSITY_PROFILE = 'University Profile'
    ATHLETIC_CLUB_PROFILE = 'Athletic Club Profile'
    GYM_PROFILE = 'Gym Profile'
    DOCTOR_PROFILE = 'Doctor Profile'
    SHOP_PROFILE = 'Shop Profile'
    APPOINTMENT = 'Appointment'


class Method(str, enum.Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    PATCH = 'patch'


class ConversationRole(str, enum.Enum):
    ADMIN = 'Admin'
    MEMBER = 'Member'
    VIEWER = 'Viewer'


class UniversityProfileRole(str, enum.Enum):
    ADMIN = 'Admin'


class DoctorProfileRole(str, enum.Enum):
    ADMIN = 'Admin'


class GymProfileRole(str, enum.Enum):
    ADMIN = 'Admin'


class ShopProfileRole(str, enum.Enum):
    ADMIN = 'Admin'


class AthleticClubProfileRole(str, enum.Enum):
    ADMIN = 'Admin'


class AppointmentRole(str, enum.Enum):
    PERSON_IN_CHARGE = 'Person in charge'
    ATTENDEE = 'Attendee'


class BaseProfileTemplateAction(str, enum.Enum):
    ADD_APPOINTMENT = 'Add appointment'
    ADD_TIME_SLOTS = 'Add time slots'
    ADD_EXCLUSION_TIMEFRAMES = 'Add exclusion timeframes'
    ADD_EXCLUSION_DATES = 'Add exclusion dates'
    SET_EXCLUSION_DATE = 'Set exclusion date'
    SET_EXCLUSION_TIMEFRAME = 'Set exclusion timeframe'
    SET_CUSTOM_DATE = 'Set custom date'


@extend_enum(BaseProfileTemplateAction)
class UniversityProfileAction(str, enum.Enum):
    pass


@extend_enum(BaseProfileTemplateAction)
class DoctorProfileAction(str, enum.Enum):
    pass


@extend_enum(BaseProfileTemplateAction)
class GymProfileAction(str, enum.Enum):
    pass


@extend_enum(BaseProfileTemplateAction)
class ShopProfileAction(str, enum.Enum):
    pass


@extend_enum(BaseProfileTemplateAction)
class AthleticClubProfileAction(str, enum.Enum):
    pass


@enum.unique
class I18nLanguage(str, enum.Enum):
    EN = 'en'
    VI = 'vi'

    @classmethod
    def to_str_list(cls):
        return [cls.EN.value, cls.VI.value]
