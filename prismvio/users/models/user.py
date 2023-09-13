from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from prismvio.core import languages
from prismvio.core.configs import CURRENCY, DEFAULT_CURRENCY
from prismvio.users.managers import UserManager


class User(AbstractUser):
    PERSONAL_PROFILE = 1
    INFLUENCER_PROFILE = 2
    BUSINESS_PROFILE = 3
    PROFILE_TYPE_CHOICES = [
        (PERSONAL_PROFILE, "Personal profile"),
        (INFLUENCER_PROFILE, "Influencer profile"),
        (BUSINESS_PROFILE, "Business profile"),
    ]

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
    country_code = models.CharField(max_length=5, default=settings.DEFAULT_COUNTRY_CODE)
    country_phone = models.CharField(max_length=5, default=settings.DEFAULT_COUNTRY_PHONE)
    verified_email_at = models.DateTimeField(_("Verified Email"), null=True, blank=True)
    verified_phone_number_at = models.DateTimeField(_("Verified Phone Number"), null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False, help_text="check user login google and check update user")

    first_name = models.CharField(max_length=45, null=True, blank=True)
    middle_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    role = models.CharField(choices=Role.choices, max_length=10, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=10, null=True)
    profile_type = models.PositiveSmallIntegerField(choices=PROFILE_TYPE_CHOICES, default=PERSONAL_PROFILE)
    marital_status = models.CharField(choices=MaritalStatus.choices, max_length=10, null=True)
    language = models.CharField(max_length=2, choices=languages.languages, default="en")

    website = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.JSONField(default=list, null=True, blank=True)
    # DEFAULT_AVATAR_URL = os.path.join(settings.STATIC_URL, 'users/avatar.jpg')

    location = models.CharField(max_length=255, null=True, blank=True)
    full_location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, null=True, blank=True)

    currency = models.CharField(
        max_length=20,
        choices=CURRENCY,
        default=DEFAULT_CURRENCY,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    business_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "username"
    REQUIRED_FIELDS = []
