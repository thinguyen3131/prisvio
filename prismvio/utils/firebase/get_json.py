import base64
import binascii
import json
from decouple import config
from loguru import logger


def get_firebase_admin_json_key(default=None):
    if default is None:
        default = {}
    firebase_admin_json = None
    # firebase_admin_base64 = os.environ.get('FIREBASE_ADMIN_BASE64_KEY', None)
    firebase_admin_base64 = config('FIREBASE_ADMIN_BASE64_KEY', None)
    if firebase_admin_base64 and not firebase_admin_json:
        try:
            firebase_admin_json = base64.b64decode(firebase_admin_base64).decode()
        except binascii.Error:
            logger.warning('Warning: The FIREBASE_ADMIN_BASE64_KEY env is not valid.')

    if firebase_admin_json:
        try:
            return json.loads(firebase_admin_json)
        except json.decoder.JSONDecodeError:
            logger.warning('Warning: The FIREBASE_ADMIN_JSON_KEY env is not valid.')

    return default
