# Generated by Django 4.2.5 on 2023-09-18 15:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("merchant", "0005_rename_location_merchant_address_merchant_country_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="merchant",
            old_name="hashtag",
            new_name="hashtags",
        ),
        migrations.RenameField(
            model_name="merchant",
            old_name="keyword",
            new_name="keywords",
        ),
    ]