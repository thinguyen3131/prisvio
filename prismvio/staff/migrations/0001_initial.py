# Generated by Django 4.2.5 on 2023-09-06 20:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("merchant", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Staff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, max_length=200, null=True)),
                ("title", models.CharField(blank=True, max_length=200, null=True)),
                ("email", models.EmailField(blank=True, max_length=255, null=True)),
                ("phone_number", models.CharField(blank=True, max_length=45, null=True)),
                ("avatar", models.JSONField(blank=True, default=dict, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "gender",
                    models.CharField(
                        blank=True, choices=[("Male", "Male"), ("Female", "Female")], max_length=50, null=True
                    ),
                ),
                (
                    "invite_status",
                    models.CharField(
                        blank=True,
                        choices=[("Pending", "Pending"), ("Accepted", "Accepted")],
                        default=None,
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "link_status",
                    models.CharField(
                        blank=True,
                        choices=[("Unlinked", "Unlinked"), ("Linked", "Linked")],
                        default="Unlinked",
                        max_length=50,
                        null=True,
                    ),
                ),
                ("price", models.FloatField(blank=True, null=True)),
                ("country_code", models.CharField(blank=True, max_length=4, null=True)),
                ("country_number", models.CharField(blank=True, max_length=4, null=True)),
                ("platform_number", models.CharField(blank=True, max_length=45, null=True)),
                ("is_show", models.BooleanField(default=True)),
                ("is_require_service", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("total_bookings", models.IntegerField(blank=True, default=0, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "merchant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="staff",
                        to="merchant.merchant",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
