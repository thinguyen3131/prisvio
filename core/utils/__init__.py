# import asyncio
# import base64
# import binascii
# import functools
# import json
# import os
# import random
# import re
# import string
# import time
# from datetime import datetime, timedelta
# from socket import gaierror
# from typing import Callable

from django.conf import settings
from django.core import exceptions
from django.core.serializers import serialize
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _

# import phonenumbers
# from asgiref.sync import async_to_sync
from cryptography.fernet import Fernet
# from loguru import logger
# from phonenumbers import region_code_for_country_code
from rest_framework.exceptions import ValidationError
from sonyflake.sonyflake import lower_16bit_private_ip

from core.utils.enums import I18nLanguage

replacement = ['=', '_E_Q']


# def timeit():
#     def wrapper(func):
#         if asyncio.iscoroutinefunction(func):
#             @functools.wraps(func)
#             async def wrapped(*args, **kwargs):
#                 start = time.time()
#                 result = await func(*args, **kwargs)
#                 end = time.time()
#                 logger.info("Function '{}.{}' executed in {:f} s",
#                             func.__module__,
#                             func.__qualname__,
#                             end - start,
#                             )
#                 return result
#         else:
#             def wrapped(*args, **kwargs):
#                 start = time.time()
#                 result = func(*args, **kwargs)
#                 end = time.time()
#                 logger.info("Function '{}.{}' executed in {:f} s",
#                             func.__module__,
#                             func.__qualname__,
#                             end - start,
#                             )
#                 return result

#         return wrapped

#     return wrapper


# def validate_phone_number(value: str, country_code=None):
#     msg = _('Invalid phone number format.')
#     try:
#         phone = phonenumbers.parse(value, country_code)
#         if not phone.country_code:
#             raise ValidationError(msg)
#         if not country_code:
#             country_code = region_code_for_country_code(phone.country_code)
#     except Exception:
#         raise ValidationError(msg)
#     if country_code and not phonenumbers.is_valid_number_for_region(phone, country_code):
#         raise ValidationError(msg)
#     value = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)

#     return value


# def get_country_code_from_phone_number(value: str):
#     msg = _('Invalid phone number format.')
#     try:
#         phone = phonenumbers.parse(value)
#     except Exception:
#         raise ValidationError(msg)

#     return region_code_for_country_code(phone.country_code)


# def merge_dicts(dict1, dict2):
#     """recursive merge dict"""
#     for k in set(dict1.keys()).union(dict2.keys()):
#         if k in dict1 and k in dict2:
#             if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
#                 yield (k, dict(merge_dicts(dict1[k], dict2[k])))
#             else:
#                 yield (k, dict2[k])
#         elif k in dict1:
#             yield (k, dict1[k])
#         else:
#             yield (k, dict2[k])


# def random_encrypted_password():
#     lower = string.ascii_lowercase
#     upper = string.ascii_uppercase
#     num = string.digits
#     password_length = settings.FIREBASE_SERVICE_PASS_LEN
#     random_str_arr = random.sample(lower + upper + num, password_length)
#     password = ''.join(random_str_arr)
#     secret_key = str.encode(settings.FIREBASE_SERVICE_PASS_KEY)
#     f = Fernet(secret_key)
#     encrypted_password = f.encrypt(password.encode()).decode()

#     return encrypted_password


# def safe_int(value):
#     """
#     Convert value to int
#     :return: int
#     """
#     try:
#         return int(value)
#     except (ValueError, TypeError):
#         return 0


def safe_bool(value):
    """
    Convert value to boolean
    :param value:
    :return: bool
    """
    if isinstance(value, bool):
        return value
    return True if str(value).lower() in ['yes', 'true', '1'] else False


# def serialize_queryset(queryset, **options):
#     """
#     Serialize queryset to json
#     :param queryset:
#     """
#     data = json.loads(serialize('json', queryset, **options))
#     rs = []
#     for item in data:
#         _item = item['fields']
#         _item['id'] = item['pk']
#         rs.append(_item)
#     return rs


# def serialize_object(obj, **options):
#     """
#     Serialize Model object to json
#     :param obj: Model object
#     :return: dict
#     """
#     foreign_keys = []
#     if options:
#         foreign_keys = options.pop('foreign_keys')

#     data = json.loads(serialize('json', [obj], **options))
#     rs = data[0]['fields']
#     rs['id'] = data[0]['pk']

#     if foreign_keys:
#         for foreign_key in foreign_keys:
#             if foreign_key not in rs:
#                 value = getattr(obj, foreign_key)
#                 if value and isinstance(value, int):
#                     rs[foreign_key] = value
#     return rs


# def decode_str(v):
#     """Decode string from base64"""
#     v = v.replace(*replacement[::-1])
#     return base64.b64decode(v).decode('utf-8')


# def async_run(func: Callable, *args, **kwargs) -> any:
#     if asyncio.iscoroutinefunction(func):
#         if settings.TESTING:
#             return asyncio.run(func(*args, **kwargs))
#         else:
#             return async_to_sync(func)(*args, **kwargs)

#     return func(*args, **kwargs)


# def get_selected_datetime_with_tz(selected_date, tz, min_time=None):
#     now = timezone.now().astimezone(tz)
#     if now.date() == selected_date and not min_time:
#         return now, now

#     if not min_time:
#         min_time = datetime.min.time()
#     dt = datetime.combine(selected_date, min_time)
#     dt_with_tz = tz.localize(dt)

#     return dt_with_tz, now


# def change_to_datetime(date, combine_time=None, date_tz=None, output_tz=None):
#     if not output_tz:
#         current_timezone = timezone.get_current_timezone()
#         output_tz = current_timezone

#     if not combine_time:
#         combine_time = datetime.min.time()
#     result = datetime.combine(date, combine_time)
#     if date_tz:
#         result = date_tz.localize(result)
#         result = result.astimezone(output_tz)
#     else:
#         result = output_tz.localize(result)

#     return result.astimezone(output_tz)


# def get_firebase_admin_json_key(default=None):
#     if default is None:
#         default = {}
#     firebase_admin_json = None
#     firebase_admin_base64 = os.environ.get('FIREBASE_ADMIN_BASE64_KEY', None)
#     if firebase_admin_base64 and not firebase_admin_json:
#         try:
#             firebase_admin_json = base64.b64decode(firebase_admin_base64).decode()
#         except binascii.Error:
#             logger.warning('Warning: The FIREBASE_ADMIN_BASE64_KEY env is not valid.')

#     if firebase_admin_json:
#         try:
#             return json.loads(firebase_admin_json)
#         except json.decoder.JSONDecodeError:
#             logger.warning('Warning: The FIREBASE_ADMIN_JSON_KEY env is not valid.')

#     return default


# def get_machine_id() -> int:
#     machine_id = safe_int(settings.MACHINE_ID)
#     if not machine_id:
#         try:
#             machine_id = lower_16bit_private_ip()
#         except gaierror:
#             return 1

#     return machine_id


# def get_period_of_time(start_time, offset):
#     if (isinstance(offset, float) or isinstance(offset, int)) and offset >= 0:
#         delta = timedelta(hours=offset)
#         result = start_time - delta
#         return result

#     return None


# def camel_to_snake_case(text):
#     s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
#     return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# def get_random_string(length=6):
#     # With combination of lower and upper case
#     result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
#     return result_str


# def validate_data_translations(data):
#     if not data or not isinstance(data, dict):
#         return

#     keys = list(data.keys())
#     languages = I18nLanguage.to_str_list()
#     for key in keys:
#         if key not in languages:
#             raise exceptions.ValidationError(f'Missing translation: {key}')
#         value = data[key]
#         if not value or not isinstance(value, str):
#             raise exceptions.ValidationError('The translation content is not valid')
