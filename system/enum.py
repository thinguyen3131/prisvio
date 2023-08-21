from enum import Enum, unique


@unique
class ScheduleStatus(str, Enum):
    RECEIVED = 'RECEIVED'
    SUCCEEDED = 'SUCCEEDED'
    CANCELED = 'CANCELED'
    FAILED = 'FAILED'
    FAILED_CANCELLATION = 'FAILED_CANCELLATION'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.RECEIVED.value, 'Received'),
            (cls.SUCCEEDED.value, 'Succeeded'),
            (cls.CANCELED.value, 'Canceled'),
            (cls.FAILED.value, 'Failed'),
            (cls.FAILED_CANCELLATION.value, 'Failed cancellation'),
        )


@unique
class EmailTemplateLanguage(str, Enum):
    ENG = 'eng'
    VIE = 'vie'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.ENG.value, 'English'),
            (cls.VIE.value, 'Vietnamese'),
        )


@unique
class SMSTemplateLanguage(str, Enum):
    ENG = 'eng'
    VIE = 'vie'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.ENG.value, 'English'),
            (cls.VIE.value, 'Vietnamese'),
        )


@unique
class EmailServiceStatus(str, Enum):
    QUEUED = 'queued'
    SENT = 'sent'
    FAILED = 'failed'
    CANCEL = 'canceled'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.QUEUED.value, 'Queued'),
            (cls.SENT.value, 'Sent'),
            (cls.FAILED.value, 'Failed'),
            (cls.CANCEL.value, 'Canceled'),
        )


@unique
class MailOutgoingStatus(str, Enum):
    NA = None
    SSL_TLS = 'ssl/tls'

    @classmethod
    def choices(cls) -> tuple:
        return (
            (cls.NA.value, None),
            (cls.SSL_TLS.value, 'SSL/TLS'),
        )


@unique
class SystemConfigDataType(str, Enum):
    INT = 'int'
    ARRAY = 'array'


@unique
class SystemConfigFolder(str, Enum):
    UPLOAD = 'upload'
    EMAIL = 'email'


@unique
class SystemConfigName(str, Enum):
    IMAGE_TYPES = 'image_types'
    MAX_IMAGE_WIDTH = 'max_image_width'
    MAX_IMAGE_HEIGHT = 'max_image_height'
    MAX_TOTAL_FILES = 'max_total_files'
    MAX_TOTAL_SIZE = 'max_total_size'
    MAX_FILE_SIZE = 'max_file_size'
    BCC_ADDRESSES = 'bcc_addresses'
