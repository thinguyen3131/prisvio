# Generated by Django 4.2.5 on 2023-09-21 07:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_bio"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]