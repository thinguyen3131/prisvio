from django.template.loader import get_template


class NotificationMessage:
    @property
    def user_id(self):
        raise NotImplementedError()

    @property
    def actor_id(self):
        return None

    @property
    def verb(self) -> str:
        raise NotImplementedError()

    @property
    def title(self) -> str:
        raise NotImplementedError()

    @property
    def content(self) -> str:
        raise NotImplementedError()

    @property
    def target_object(self):
        return None

    @property
    def template(self) -> str | None:
        return self.get_template(None)

    @property
    def payload(self) -> dict | None:
        """
        Extra payload for FCM
        :return:
        """
        return None

    def get_template(self, file_path):
        """Get content push notification from file

        Args:
            file_path: Template path

        Returns:
            str: Content push notification
        """
        if file_path:
            template_context = {}
            content = get_template(file_path).render(template_context)
            return content
        return None

    def dict(self):
        return {
            "user_id": self.user_id,
            "actor_id": self.actor_id,
            "verb": self.verb,
            "title": self.title,
            "content": self.content,
            "template": self.template,
            "payload": self.payload,
            "target_object": self.target_object,
        }
