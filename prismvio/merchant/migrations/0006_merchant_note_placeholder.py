# Generated by Django 4.2.5 on 2023-10-01 01:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("merchant", "0005_alter_merchant_latitude_alter_merchant_longitude"),
    ]

    operations = [
        migrations.AddField(
            model_name="merchant",
            name="note_placeholder",
            field=models.TextField(blank=True, help_text="Booking note for your client", null=True),
        ),
    ]
