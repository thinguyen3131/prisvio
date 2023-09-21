# Generated by Django 4.2.5 on 2023-09-18 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name_vi", models.CharField(max_length=255)),
                ("full_name_en", models.CharField(max_length=255)),
                ("zip_code", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="District",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20)),
                ("name_vi", models.CharField(max_length=255)),
                ("name_en", models.CharField(max_length=255)),
                ("zip_code", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="location.country"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Ward",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20)),
                ("name_vi", models.CharField(max_length=255)),
                ("name_en", models.CharField(max_length=255)),
                ("zip_code", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="location.country"
                    ),
                ),
                (
                    "district",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="location.district"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Province",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20)),
                ("name_vi", models.CharField(max_length=255)),
                ("name_en", models.CharField(max_length=255)),
                ("zip_code", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="location.country"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="district",
            name="province",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="location.province"
            ),
        ),
    ]