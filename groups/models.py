from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_groups")
    members = models.ManyToManyField(User, related_name="chat_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_group_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
