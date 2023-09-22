# Generated by Django 4.2.5 on 2023-09-21 16:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("merchant", "0002_initial"),
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
        migrations.AddField(
            model_name="merchant",
            name="total_bookings",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
