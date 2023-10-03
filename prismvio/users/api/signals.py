from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from prismvio.users.models.user import Friend, Friendship, PrivacySetting


@receiver(post_save, sender=Friendship)
def create_friend_objects(sender, instance, **kwargs):
    if instance.status == Friendship.ACCEPTED:
        Friend.objects.create(user=instance.sender, friend=instance.receiver)
        Friend.objects.create(user=instance.receiver, friend=instance.sender)


@receiver(post_save, sender=get_user_model())
def create_privacy_setting(sender, instance, created, **kwargs):
    if created:
        PrivacySetting.objects.create(
            user=instance,
            username_privacy=PrivacySetting.EVERYONE,
            email_privacy=PrivacySetting.EVERYONE,
            phone_number_privacy=PrivacySetting.EVERYONE,
        )
