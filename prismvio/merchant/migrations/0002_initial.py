# Generated by Django 4.2.5 on 2023-09-21 03:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("location", "0001_initial"),
        ("merchant", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="merchant",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="merchants",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="merchant",
            name="province",
            field=models.ForeignKey(
                blank=True,
                help_text="connect with Province in table Province location",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="location.province",
            ),
        ),
        migrations.AddField(
            model_name="merchant",
            name="ward",
            field=models.ForeignKey(
                blank=True,
                help_text="connect with Ward in table Ward location",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="location.ward",
            ),
        ),
        migrations.AddField(
            model_name="exclusiondate",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exclusion_date",
                to="merchant.merchant",
            ),
        ),
    ]