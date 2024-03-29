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
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name_vi", models.CharField(default="SOME STRING", max_length=50)),
                ("name_en", models.CharField(default="SOME STRING", max_length=50)),
                ("notes", models.CharField(max_length=200)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Collection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("order", models.PositiveIntegerField(default=0)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="CollectionItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Hashtag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Products",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("quantity", models.IntegerField()),
                ("unit", models.CharField(default=None, max_length=255, null=True)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                (
                    "original_price",
                    models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
                ),
                (
                    "discount_price",
                    models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
                ),
                ("images", models.JSONField(blank=True, default=list, null=True)),
                ("total_bookings", models.IntegerField(blank=True, default=0, null=True)),
                ("hidden", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Promotion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("start_date", models.DateField(null=True)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_date", models.DateField(null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                ("discount", models.FloatField(blank=True, default=None, null=True)),
                ("unit", models.CharField(default=None, max_length=255, null=True)),
                ("quantity", models.IntegerField(blank=True, default=None, null=True)),
                ("type", models.CharField(blank=True, default="discount", max_length=255, null=True)),
                ("buy_quantity", models.IntegerField(blank=True, null=True)),
                ("get_quantity", models.IntegerField(blank=True, null=True)),
                ("images", models.JSONField(blank=True, default=list, null=True)),
                ("total_bookings", models.IntegerField(blank=True, default=0, null=True)),
                ("all_day", models.BooleanField(default=False)),
                ("is_happy_hour", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Services",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, default=None, null=True)),
                ("time", models.FloatField()),
                ("time_date", models.CharField(default=None, max_length=255, null=True)),
                ("require_staff", models.BooleanField(default=False)),
                (
                    "original_price",
                    models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
                ),
                (
                    "discount_price",
                    models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=12, null=True),
                ),
                ("available_slots", models.IntegerField()),
                ("slots_unit", models.CharField(blank=True, max_length=50)),
                ("use_total_available_slots", models.BooleanField(default=False)),
                ("images", models.JSONField(blank=True, default=list, null=True)),
                ("hidden", models.BooleanField(default=False)),
                ("flexible_time", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("total_bookings", models.IntegerField(blank=True, default=0, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service",
                        to="menu_merchant.category",
                    ),
                ),
                ("hashtags", models.ManyToManyField(blank=True, related_name="service", to="menu_merchant.hashtag")),
                (
                    "merchant",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service",
                        to="merchant.merchant",
                    ),
                ),
                (
                    "owner",
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
