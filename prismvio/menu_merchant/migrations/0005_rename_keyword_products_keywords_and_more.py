# Generated by Django 4.2.5 on 2023-09-25 10:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("menu_merchant", "0004_remove_promotion_end_time_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="products",
            old_name="keyword",
            new_name="keywords",
        ),
        migrations.RenameField(
            model_name="services",
            old_name="keyword",
            new_name="keywords",
        ),
    ]
