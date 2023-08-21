from users.enums import UserSettingDataType, UserSettingKey, UserSettingLanguages

MSG_SNIPPETS = {
    'SHARE_AN_EVENT': '[:-SHARE_AN_EVENT]',
    'SHARE_PROFILE': '[:-SHARE_PROFILE]',
    'SENT_MEDIA': '[:-SENT_MEDIA]',
}


CONVERSATION_PREFIXES = {
    'PRIVATE_EVENT': 'Private •',
    'PUBLIC_EVENT': 'General •',
}


LOGURU_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<level>{process.name}</level> | '
    '<level>{thread.name}</level> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:'
    '<cyan>{line}</cyan> - <level>{message}</level>'
)


DEFAULT_USER_SETTINGS = {
    UserSettingKey.LANGUAGE.value: {
            'type': UserSettingDataType.STRING.value,
            'value': UserSettingLanguages.ENG.value,
    },
    UserSettingKey.ALLOW_NOTIFICATIONS.value: {
            'type': UserSettingDataType.BOOL.value,
            'value': True,
    },
}

URL_GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
URL_GOOGLE_ME = "https://people.googleapis.com/v1/people/me"
