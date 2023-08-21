import hashlib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from users.enums import IntervalLockTime, MaxTime, OTPAction, OTPType

User = get_user_model()


def generate_signature(*args):
    text = ''
    for item in args:
        text += str(item)
    signature = '%s%s%s' % (text, settings.SECRET_KEY, timezone.now())
    signature = hashlib.md5(signature.encode('utf-8')).hexdigest()
    return signature


class OneTimePasswordManager(models.Manager):
    def get_by_email(self, email, signature, otp_action):
        now = timezone.now()
        past_time = now - timedelta(minutes=IntervalLockTime.SEND.value)
        return self.filter(
            signature=signature,
            otp_type=OTPType.EMAIL.value,
            email=email,
            otp_action=otp_action,
            is_verified=True,
            last_send__gte=past_time,
            is_used=False,
        ).last()


class OneTimePassword(models.Model):
    user = models.ForeignKey(User, related_name='otp_set',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True, db_index=True)
    phone_number = models.CharField(max_length=45, null=True, blank=True,
                                    db_index=True)
    signature = models.CharField(max_length=32, db_index=True)
    send_counter = models.PositiveSmallIntegerField(default=0)
    last_send = models.DateTimeField(default=timezone.now)
    check_counter = models.PositiveSmallIntegerField(default=0)
    last_check = models.DateTimeField(default=timezone.now)
    otp_type = models.CharField(max_length=30, db_index=True, default=OTPType.PHONE_NUMBER)
    otp_action = models.CharField(max_length=30, db_index=True, default=OTPAction.ID_VERIFICATION)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)

    objects = OneTimePasswordManager()

    def save(self, *args, **kwargs):
        if not self.pk or not self.signature:
            self.refresh_signature(False)
        super(OneTimePassword, self).save(*args, **kwargs)

    def refresh_signature(self, commit=True):
        self.signature = generate_signature(self.user_id)
        if commit:
            self.save()

    def update_status(self):
        duration = self.get_duration(self.last_send)
        if duration < IntervalLockTime.CHECK:
            self.send_counter += 1
        else:
            self.send_counter = 1
            self.last_send = timezone.now()
        self.is_verified = False
        self.is_used = False
        self.save()

    def get_duration(self, last):
        now = timezone.now()
        delta = now - last
        return delta.seconds

    def can_request_otp(self):
        duration = self.get_duration(self.last_send)
        if duration > IntervalLockTime.SEND:
            self.send_counter = 0
            self.save()
            return True
        return self.send_counter < MaxTime.SEND

    def can_check_otp(self):
        duration = self.get_duration(self.last_check)
        if duration > IntervalLockTime.CHECK:
            self.check_counter = 1
            self.last_check = timezone.now()
            allowed = True
        else:
            self.check_counter += 1
            allowed = self.check_counter <= MaxTime.CHECK
        self.save()
        return allowed
