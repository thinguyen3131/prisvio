import time
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from prismvio.users.managers import UserManager


class User(AbstractUser):
    class Gender(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        OTHERS = "Others"

    class MaritalStatus(models.TextChoices):
        MARRIED = "MR"
        SINGLE = "SI"
        SEPARATED = "SE"
        DIVORCE = "DV"
        OTHERS = "OT"

    class Role(models.TextChoices):
        ADMIN = "Admin"
        INFLUENCER = "Influencer"
        PARTNER = "Partner"
        USER = "User"

    username = models.CharField(unique=True, blank=True, null=True, max_length=150)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    verified_email_at = models.DateTimeField(_("Verified Email"), null=True, blank=True)
    verified_phone_number_at = models.DateTimeField(_("Verified Phone Number"), null=True, blank=True)

    first_name = models.CharField(max_length=45, null=True, blank=True)
    middle_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(choices=Role.choices, max_length=10, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=10, null=True)
    marital_status = models.CharField(choices=MaritalStatus.choices, max_length=10, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    business_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class UserSocialAuth(models.Model):
    """Custom Social Auth association model"""

    SYNC_START_TIMEDELTA = timedelta(weeks=4)
    SYNC_END_TIMEDELTA = timedelta(weeks=8)

    user = models.ForeignKey("users.User", related_name="social_data", on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=255, blank=True, null=True)
    extra_data = JSONField()
    calendar_data = JSONField(default=dict)
    subscription_id = models.CharField(max_length=255, null=True, db_index=True)

    @property
    def email(self) -> str:
        extra_data = self.extra_data
        return extra_data.get("email")

    def check_expire_access_token(self):
        extra_data = self.extra_data
        auth_time = extra_data.get("auth_time")
        expires_in = extra_data.get("expires_in")
        if auth_time and expires_in:
            expire_day = auth_time + expires_in
            now = int(time.time())
            return now > expire_day

        return True

    def access_token(self):
        extra_data = self.extra_data
        return extra_data.get("access_token")
