class Const(object):
    choices = []

    def __setattr__(self, *_):
        raise Exception('Can not set value for const')

    @classmethod
    def get_value(cls, name):
        name = name.lower()
        for item in cls.choices:
            if item[1].lower() == name:
                return item[0]

    @classmethod
    def get_name(cls, value):
        if not isinstance(value, int):
            value = int(value)
        for item in cls.choices:
            if item[0] == value:
                return item[1]


class CODEBASE(Const):
    EXISTED = 'existed'
    FORMAT_INVALID = 'format_invalid'
    PARAM_MISSING = 'param_missing'
    INVALID = 'invalid'
    NOT_FOUND = 'not_found'
    PERMISSION_DENIED = 'permission_denied'
    SERVER_ERROR = 'server_error'


class CODE(CODEBASE):
    class AUTH(Const):
        CREDENTIAL_MISSING = 'credential_missing'
        CREDENTIAL_INVALID = 'credential_invalid'
        TOKEN_EXPIRED = 'token_expired'

    class USER(Const):
        DISABLED = 'user_disabled'
        NOT_VERIFIED = 'user_not_verified'
        OTP_INVALID = 'otp_invalid'
        OTP_NOT_FOUND = 'otp_not_found'
        OTP_SIGNAL_INVALID = 'otp_signal_invalid'
        OTP_REQUEST_LIMITED = 'otp_request_limited'
        MISSING_EMAIL_OR_PHONE = 'missing_email_or_phone'
        MISSING_FIELD_VERIFIED = 'missing_field_verified'
        INVALID_ID_TOKEN = 'invalid_id_token'
        EXPIRED_ID_TOKEN = 'expired_id_token'

    class GCS(Const):
        GCS_UPLOAD_SIGNED_URL = "upload_signed_url"
        GCS_MISSING_FILE_NAME = "missing_file_name"
        GCS_MISSING_FILE_TYPE = "missing_file_type"
