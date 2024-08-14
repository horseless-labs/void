# Generated by Django 5.0.7 on 2024-08-14 12:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0003_conversation_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="message",
            name="conversation",
        ),
        migrations.AddField(
            model_name="message",
            name="chat_id",
            field=models.CharField(default="default_chat_id", max_length=64),
            preserve_default=False,
        ),
    ]
