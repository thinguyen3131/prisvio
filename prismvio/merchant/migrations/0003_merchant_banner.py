# Generated by Django 4.2.5 on 2023-09-26 07:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("merchant", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="merchant",
            name="banner",
            field=models.JSONField(blank=True, default=dict, help_text="Banner", null=True),
        ),
    ]