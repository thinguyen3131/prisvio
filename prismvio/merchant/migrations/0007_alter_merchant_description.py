# Generated by Django 4.2.5 on 2023-10-02 08:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("merchant", "0006_merchant_note_placeholder"),
    ]

    operations = [
        migrations.AlterField(
            model_name="merchant",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]