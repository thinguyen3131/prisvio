# Generated by Django 4.2.5 on 2023-09-27 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0002_remove_booking_booked_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="merchant_info",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]