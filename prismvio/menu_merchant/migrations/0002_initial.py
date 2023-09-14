# Generated by Django 4.2.5 on 2023-09-14 03:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("staff", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("merchant", "0001_initial"),
        ("menu_merchant", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="services",
            name="merchant",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, related_name="service", to="merchant.merchant"
            ),
        ),
        migrations.AddField(
            model_name="services",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="services",
            name="staff",
            field=models.ManyToManyField(blank=True, related_name="service", to="staff.staff"),
        ),
        migrations.AddField(
            model_name="promotion",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="promotion",
                to="merchant.merchant",
            ),
        ),
        migrations.AddField(
            model_name="promotion",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="promotion",
            name="products",
            field=models.ManyToManyField(blank=True, related_name="promotions", to="menu_merchant.products"),
        ),
        migrations.AddField(
            model_name="promotion",
            name="services",
            field=models.ManyToManyField(blank=True, related_name="promotions", to="menu_merchant.services"),
        ),
        migrations.AddField(
            model_name="products",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="menu_merchant.category",
            ),
        ),
        migrations.AddField(
            model_name="products",
            name="hashtags",
            field=models.ManyToManyField(blank=True, related_name="products", to="menu_merchant.hashtag"),
        ),
        migrations.AddField(
            model_name="products",
            name="keyword",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="menu_merchant.keyword",
            ),
        ),
        migrations.AddField(
            model_name="products",
            name="merchant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="merchant.merchant",
            ),
        ),
        migrations.AddField(
            model_name="products",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="collectionitem",
            name="collection",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="menu_merchant.collection"),
        ),
        migrations.AddField(
            model_name="collectionitem",
            name="product",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="menu_merchant.products"
            ),
        ),
        migrations.AddField(
            model_name="collectionitem",
            name="service",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="menu_merchant.services"
            ),
        ),
        migrations.AddField(
            model_name="collection",
            name="merchant",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collection",
                to="merchant.merchant",
            ),
        ),
        migrations.AddField(
            model_name="collection",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="hashtag",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="category",
                to="menu_merchant.hashtag",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="category",
                to="menu_merchant.category",
            ),
        ),
    ]
