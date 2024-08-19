from django.db import models
from django.contrib.auth.models import User

from .services import chat_session

# Create your models here.

class Conversation(models.Model):
    chat_id = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def initialize_chat(self, username=None, chat_id=None):
        self.base_messages = chat_session.initialize_chat_session()
        # if chat_id == None:
        #     self.chat_id = chat_session.generate_chat_id()
        # else:
        #     self.chat_id = chat_id
        self.chat_id = chat_session.generate_chat_id()

        self.save()

        for message_data in self.base_messages:
            role = message_data["role"]
            content = message_data["content"]

            user = None
            if role == "user":
                user = User.objects.get(username=username)
            
            message = Message.objects.create(
                user=user,
                # conversation=self,
                chat_id=self.chat_id,
                role=role,
                body=content
            )
            message.save()

    def save(self, *args, **kwargs):
        if not self.chat_id:
            self.chat_id = chat_session.generate_chat_id()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Conversation {self.chat_id}"
    
class Message(models.Model):
    ROLE_CHOICES = [
        ("system", "System"),
        ("agent", "Agent"),
        ("user", "User")
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    # conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=64)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)