import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import JSONField
from django.db import models

from notifications import choices


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verb = models.CharField(max_length=100)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="actor",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="receiver",
        on_delete=models.CASCADE,
    )

    topic = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    content = models.CharField(max_length=250, null=True, blank=True)
    template = models.CharField(max_length=250, null=True, blank=True, help_text="Message template")
    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=choices.MESSAGE_STATUS_CHOICES,
        default=choices.MESSAGE_STATUS_SENT,
    )
    payload = JSONField(null=True, blank=True)
    read = models.BooleanField(default=False)
    visible = models.BooleanField(default=True, help_text="Visible to user?")

    """
    Generic foreign keys to other models
    """
    target_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="target_object",
        null=True,
        blank=True,
    )
    target_id = models.IntegerField(null=True, blank=True)
    target_object = GenericForeignKey("target_type", "target_id")

    memo = models.CharField(max_length=250, null=True, blank=True, help_text="Internal Notes")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "visible"]),
        ]

        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.content

    def mark_as_read(self):
        self.read = True
        self.save()
