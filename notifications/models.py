from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("message", "New Message"),
        ("group_message", "New Group Message"),
        ("group_add", "Added to Group"),
        ("group_remove", "Removed from Group"),
        ("group_delete", "Group Deleted"),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    text = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient.username}: {self.text[:30]}"
    
class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Push subscription for {self.user.username}"
