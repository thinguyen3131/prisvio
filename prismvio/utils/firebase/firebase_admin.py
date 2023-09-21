import firebase_admin
from django.conf import settings
from firebase_admin import App, credentials


class FailedCreateChatRoomException(Exception):
    pass


class FirebaseAdminService:
    default_app: App
    secret_key: bytes
    password_length: int
    rooms_key: str
    messages_key: str
    profiles_key: str

    def __init__(self):
        cert = settings.FIREBASE_ADMIN_JSON_KEY
        database_url = settings.FIREBASE_DB_URL
        if not cert:
            raise Exception("The FIREBASE_ADMIN_JSON_KEY environment variable is not set.")
        if not database_url:
            raise Exception("The FIREBASE_DB_URL environment variable is not set.")

        cred = credentials.Certificate(cert)
        self.default_app = firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": database_url,
                "databaseAuthVariableOverride": {
                    "uid": settings.FIREBASE_DB_AUTH_UID,
                },
            },
        )
        self.secret_key = str.encode(settings.FIREBASE_SERVICE_PASS_KEY)
        self.password_length = settings.FIREBASE_SERVICE_PASS_LEN
