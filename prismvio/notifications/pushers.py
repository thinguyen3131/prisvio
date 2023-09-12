from typing import Optional

from fcm_django.models import FCMDevice


class FireBasePusher:
    @classmethod
    def get_user_devices(cls, user):
        if not user:
            return []
        return FCMDevice.objects.filter(user=user)

    def send(self, message: dict, badge: Optional[int] = None) -> bool:
        user = message.get('user_id', None)
        devices = self.get_user_devices(user)
        if not devices.exists():
            return False
        content = message.get('content', '')
        template = message.get('template', '')
        title = message.get('title', '')
        data = message.get('payload')
        if template:
            content = template
        devices.send_message(title=title, body=content, badge=badge, data=data, sound="default")
        return True
