# Generated by Django 4.1.2 on 2024-09-14 16:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0002_alter_user_groups_alter_user_user_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                default="image/avatar.svg", null=True, upload_to=""
            ),
        ),
    ]
