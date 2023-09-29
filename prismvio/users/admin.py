from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from prismvio.users.models.user import PrivacySetting

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("email","phone_number", "password")}),
        (_("Personal info"), {"fields": ("full_name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        )  # ,
        # (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["id", "email", "phone_number", "full_name", "is_superuser"]
    search_fields = ["id", "email", "phone_number", "full_name"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_per_page = 20


@admin.register(PrivacySetting)
class PrivacySettingAdmin(admin.ModelAdmin):
    list_display = ["user", "username_privacy", "email_privacy", "phone_number_privacy"]
    # list_filter = ['user']
    search_fields = ["user", "username_privacy", "email_privacy", "phone_number_privacy"]
    list_per_page = 20
