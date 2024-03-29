# Generated by Django 4.2.5 on 2023-09-06 19:58

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EmailTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.SlugField(max_length=100)),
                (
                    "language",
                    models.CharField(choices=[("eng", "Eng"), ("vie", "Vie")], default="eng", max_length=100),
                ),
                ("use_mjml", models.BooleanField(default=True)),
                ("mjml", models.TextField(blank=True, default="", null=True)),
                ("html", tinymce.models.HTMLField(blank=True, default="", null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("code", "language")},
            },
        ),
    ]
