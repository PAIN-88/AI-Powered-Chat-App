from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification

def send_notification(recipient, notification_type, text, link="", sender = None):

    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        text=text,
        link=link,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notification_{recipient.id}",
        {
            "type":"send_notification",
            "notification" :{
                "id": notification.id,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "link":notification.link,
                "is_read": notification.is_read,
                "created_at": notification.created_at.strftime("%b %d, %I:%M %p"),
            },
        }
    )
    return notification