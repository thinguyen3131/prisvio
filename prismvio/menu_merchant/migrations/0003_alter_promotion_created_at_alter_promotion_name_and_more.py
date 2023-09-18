# Generated by Django 4.2.5 on 2023-09-13 03:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("menu_merchant", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="promotion",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="promotion",
            name="name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="promotion",
            name="products",
            field=models.ManyToManyField(related_name="promotions", to="menu_merchant.products"),
        ),
        migrations.AlterField(
            model_name="promotion",
            name="services",
            field=models.ManyToManyField(related_name="promotions", to="menu_merchant.services"),
        ),
        migrations.AlterField(
            model_name="promotion",
            name="unit",
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="promotion",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]