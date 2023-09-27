# Generated by Django 4.2.5 on 2023-09-26 09:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu_merchant", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="sold_quantity",
            field=models.IntegerField(default=0, help_text="Product sold quantity"),
        ),
        migrations.AddField(
            model_name="service",
            name="sold_quantity",
            field=models.IntegerField(blank=True, default=0, help_text="Service sold quantity", null=True),
        ),
    ]