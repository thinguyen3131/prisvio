# Generated by Django 4.2.5 on 2023-09-26 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("menu_merchant", "0003_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("merchant", "0003_merchant_banner"),
        ("staff", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField(blank=True, default=None, null=True)),
                ("end_date", models.DateField(blank=True, default=None, null=True)),
                ("total_price", models.FloatField(blank=True, default=None, null=True)),
                ("note", models.TextField(blank=True, default=None, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Upcoming", "Upcoming"),
                            ("Ongoing", "Ongoing"),
                            ("Completed", "Completed"),
                            ("Canceled", "Canceled"),
                        ],
                        default="Upcoming",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Cash", "Cash"),
                            ("Momo", "Momo"),
                            ("Zalo Pay", "Zalo Pay"),
                            ("Bank_Transfer", "Bank Transfer"),
                        ],
                        default="Cash",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("deleted_at", models.DateTimeField(blank=True, default=None, null=True)),
                ("cancel_reason", models.TextField(blank=True, default=None, null=True)),
                ("sent_notify", models.IntegerField(default=0)),
                ("user_info", models.JSONField(blank=True, default=dict, null=True)),
                (
                    "booked_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="booked_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "booked_user",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="booked_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "cancel_by",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "merchant",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="merchant.merchant"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookingService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("service_name", models.CharField(blank=True, max_length=200, null=True)),
                ("start_date", models.DateTimeField(blank=True, default=None, null=True)),
                ("end_date", models.DateTimeField(blank=True, default=None, null=True)),
                ("duration", models.IntegerField(blank=True, default=None, null=True)),
                ("price", models.FloatField(blank=True, default=None, null=True)),
                ("quantity", models.IntegerField(blank=True, default=None, null=True)),
                ("note", models.TextField(blank=True, default=None, null=True)),
                ("is_anyone", models.BooleanField(default=False)),
                ("service_info", models.JSONField(blank=True, default=dict, null=True)),
                ("staff_info", models.JSONField(blank=True, default=dict, null=True)),
                ("merchant_info", models.JSONField(blank=True, default=dict, null=True)),
                ("user_info", models.JSONField(blank=True, default=dict, null=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bookings.booking")),
                (
                    "service",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="menu_merchant.service"
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="staff.staff"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookingPromotion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price", models.FloatField(blank=True, default=0, null=True)),
                ("unit", models.CharField(blank=True, max_length=100, null=True)),
                ("promotion_info", models.JSONField(blank=True, default=dict, null=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bookings.booking")),
                (
                    "promotion",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="menu_merchant.promotion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BookingProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.IntegerField(blank=True, default=None, null=True)),
                ("price", models.FloatField(blank=True, default=None, null=True)),
                ("product_info", models.JSONField(blank=True, default=dict, null=True)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bookings.booking")),
                (
                    "product",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="menu_merchant.product"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="booking",
            name="products",
            field=models.ManyToManyField(
                blank=True, related_name="products", through="bookings.BookingProduct", to="menu_merchant.product"
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="promotions",
            field=models.ManyToManyField(
                blank=True,
                related_name="promotions",
                through="bookings.BookingPromotion",
                to="menu_merchant.promotion",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="services",
            field=models.ManyToManyField(
                blank=True, related_name="services", through="bookings.BookingService", to="menu_merchant.service"
            ),
        ),
    ]
