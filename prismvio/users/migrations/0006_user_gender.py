# Generated by Django 4.2.5 on 2023-10-02 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_remove_user_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="gender",
            field=models.SmallIntegerField(
                choices=[(0, "Not known"), (1, "Male"), (2, "Female"), (9, "Not applicable")], null=True
            ),
        ),
    ]