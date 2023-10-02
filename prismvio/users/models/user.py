from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from prismvio.core import languages
from prismvio.core.configs import CURRENCY, DEFAULT_CURRENCY
from prismvio.location.models import Country, District, Province, Ward
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
    PROFILE_FIELDS_MAP = {
        PERSONAL_PROFILE: {
            "applicable": ("first_name", "middle_name", "last_name", "birth_date", "full_name"),
            "not_applicable": ("brand_name",),
            "required": ("full_name",),
        },
        INFLUENCER_PROFILE: {
            "applicable": ("first_name", "middle_name", "last_name", "birth_date", "brand_name"),
            "not_applicable": (),
            "required": ("brand_name",),
        },
        BUSINESS_PROFILE: {
            "applicable": ("brand_name", "birth_date"),
            "not_applicable": ("first_name", "middle_name", "last_name"),
            "required": ("brand_name",),
        },
    }

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
    country_code = models.CharField(max_length=5, default=settings.DEFAULT_COUNTRY_CODE)   # vn
    country_phone = models.CharField(max_length=5, default=settings.DEFAULT_COUNTRY_PHONE)  #+84
    verified_email_at = models.DateTimeField(_("Verified Email"), null=True, blank=True)
    verified_phone_number_at = models.DateTimeField(_("Verified Phone Number"), null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False, help_text="check user login google and check update user")

    first_name = models.CharField(max_length=45, null=True, blank=True)
    middle_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    brand_name = models.CharField(max_length=255, null=True, blank=True)

    role = models.CharField(choices=Role.choices, max_length=10, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=10, null=True)
    profile_type = models.PositiveSmallIntegerField(choices=PROFILE_TYPE_CHOICES, default=PERSONAL_PROFILE)
    marital_status = models.CharField(choices=MaritalStatus.choices, max_length=10, null=True)
    language = models.CharField(max_length=2, choices=languages.languages, default="en")

    website = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.JSONField(default=dict, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)

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
    birth_date = models.DateField(null=True, blank=True)

    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    banner = JSONField(default=dict, null=True, blank=True, help_text="Banner")
    is_share_phone = models.BooleanField(default=False, null=True, blank=True)
    categories = models.ManyToManyField(
        "menu_merchant.Category", related_name="categories", blank=True, help_text="Your favorite Categories"
    )

    ward = models.ForeignKey(Ward, null=True, blank=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District, null=True, blank=True, on_delete=models.SET_NULL)
    province = models.ForeignKey(Province, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return " ".join(
            [
                getattr(self, x) if getattr(self, x) else ""
                for x in self.PROFILE_FIELDS_MAP[self.profile_type]["required"]
            ]
        )

    def set_status_active(self, status: bool):
        if status is True:
            self.__activate()
        else:
            self.__deactivate()

    def __deactivate(self):
        self.is_active = False
        self.save()
        # todo: add celery task here to process post-deactivate

    def __activate(self):
        self.is_active = True
        self.save()
        # todo: add celery task here to process post-activate

    def friend_ids(self):
        return self.friends.all().values_list("friend_id", flat=True).distinct()

    # def get_all_parents(self, user, parent_ids):
    #     if user.parent:
    #         parent_ids.add(user.parent_id)
    #         self.get_all_parents(user.parent, parent_ids)
    #     return parent_ids
    
    # def parent_ids(self):
    #     parent_ids_set = set()
    #     if self.parent:
    #         parent_ids_set = self.get_all_parents(self.parent, parent_ids_set)
    #     return list(parent_ids_set)


class PrivacySetting(models.Model):
    ONLY_ME = "OM"
    EVERYONE = "EV"
    FRIENDS = "FR"
    PRIVACY_CHOICES = [
        (ONLY_ME, "Only Me"),
        (EVERYONE, "Everyone"),
        (FRIENDS, "Friends"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="privacy_settings")
    username_privacy = models.CharField(max_length=2, choices=PRIVACY_CHOICES, default=EVERYONE)
    email_privacy = models.CharField(max_length=2, choices=PRIVACY_CHOICES, default=EVERYONE)
    phone_number_privacy = models.CharField(max_length=2, choices=PRIVACY_CHOICES, default=EVERYONE)

    def __str__(self):
        return f"Privacy settings for {self.user.username}"


class Friendship(models.Model):
    PENDING = "PE"
    ACCEPTED = "AC"
    DECLINED = "DE"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DECLINED, "Declined"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
        help_text="the person sending the friend request",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
        help_text="friend recipient",
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.get_status_display()}"


class Friend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="friends", on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_friends", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "friend")
