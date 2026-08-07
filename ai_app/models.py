from django.db import models
from django.contrib.auth.models import User

class AIConversation(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_messages")
    role = models.CharField(max_length=10, choices=[("user", "User"), ("ai", "AI")])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        indexes = [models.Index(fields=["user", "timestamp"])]
        

