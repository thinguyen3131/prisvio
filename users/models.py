from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        if not username and not email and not phone_number:
            raise ValueError('At least one of username, email, or phone number is required.')
        if not password:
            raise ValueError('Password is required.')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username=None, email=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username=username, email=email, phone_number=phone_number, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Gender(models.TextChoices):
        MALE = 'Male'
        FEMALE = 'Female'
        OTHERS = 'Others'

    class MaritalStatus(models.TextChoices):
        MARRIED = 'MR'
        SINGLE = 'SI'
        SEPARATED = 'SE'
        DIVORCE = 'DV'
        OTHERS = 'OT'

    class Role(models.TextChoices):
        ADMIN = "Admin"
        INFLUENCER = "Influencer"
        PARTNER = "Partner"
        USER = "User"

    username = models.CharField(unique=True, blank=True, null=True, max_length=150)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    role = models.CharField(choices=Role.choices, max_length=10, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=10, null=True)
    marital_status = models.CharField(choices=MaritalStatus.choices, max_length=10, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
