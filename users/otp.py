import base64
import datetime
import hashlib
from django.conf import settings
from loguru import logger
from pyotp import TOTP

__all__ = [
    'OTPError', 'LimitedError', 'InvalidOTPError', 'INTERVAL_TIME', 'get_secret_key', 'generate_otp',
    'is_valid_otp', 'is_valid_otp_instance', 'is_valid_otp_and_signature',
    'get_otp_instance', 'require_new_otp',
]

from users.models import OneTimePassword


class OTPError(Exception):
    pass


class LimitedError(OTPError):
    pass


class InvalidOTPError(OTPError):
    pass


# Interval time of OTP in sec
INTERVAL_TIME = 60 * 2


def log(content):
    content = 'USER_OTP ' + content
    logger.error(content)


def get_secret_key(signature):
    user_key = '%s_%s' % (signature, settings.SECRET_KEY)
    user_key = hashlib.md5(user_key.encode('utf-8')).hexdigest()
    key = base64.b32encode(user_key.encode('utf-8'))
    return key[:16].decode('utf-8')


def generate_otp(signature=None, interval=INTERVAL_TIME, for_time=None):
    key = get_secret_key(signature)
    totp = TOTP(str(key), interval=interval)
    if for_time is None:
        for_time = datetime.datetime.now().replace(microsecond=0)
    code = totp.at(for_time)
    log('generate_otp: Code=%s, sig=%s, input=%s' % (code, signature, for_time))
    return code


def is_valid_otp(otp, signature=None, interval=INTERVAL_TIME, for_time=None):
    key = get_secret_key(signature)
    totp = TOTP(str(key), interval=interval)
    result = totp.verify(otp, for_time=for_time, valid_window=1)
    log('is_valid_otp: Rs=%s, Code=%s, S=%s, Key=%s, Interval=%s \n' % (result, otp, signature, key, interval))
    return result


def is_valid_otp_instance(instance, otp, interval=INTERVAL_TIME):
    if not instance.can_check_otp():
        raise LimitedError('Check OTP is limited, please wait a moment.')
    return is_valid_otp(otp, instance.signature, interval=interval)


def get_otp_instance(signature,
                     otp_type=None,
                     otp_action=None):
    try:
        params = dict(signature=signature)
        if otp_type:
            params.update(otp_type=otp_type)
        if otp_action:
            params.update(otp_action=otp_action)

        return OneTimePassword.objects.get(**params)
    except OneTimePassword.DoesNotExist:
        return None


def is_valid_otp_and_signature(otp, signature, otp_type=None):
    instance = get_otp_instance(signature=signature, otp_type=otp_type)
    if not instance or not is_valid_otp_instance(instance, otp):
        raise InvalidOTPError('Invalid OTP or signature')
    return instance


def require_new_otp(instance, interval=INTERVAL_TIME):
    if not instance.can_request_otp():
        raise LimitedError('Can not request more OTP.')
    instance.refresh_signature(False)
    otp = generate_otp(instance.signature, interval=interval)
    instance.update_status()
    return otp, instance.signature
