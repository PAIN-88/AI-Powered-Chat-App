import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from pywebpush import webpush, WebPushException
from .models import Notification, PushSubscription


def send_web_push(subscription, payload):
    try:
        webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"},
        )
    except WebPushException as ex:
        status = getattr(ex.response, "status_code", None)
        if status in (404, 410):
            subscription.delete()


def send_notification(recipient, notification_type, text, link="", sender=None):

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
            "type": "send_notification",
            "notification": {
                "id": notification.id,
                "notification_type": notification.notification_type,
                "text": notification.text,
                "link": notification.link,
                "is_read": notification.is_read,
                "created_at": notification.created_at.strftime("%b %d, %I:%M %p"),
            },
        }
    )

    push_payload = {"title": "PAIN Chat", "body": text, "link": link}
    for subscription in PushSubscription.objects.filter(user=recipient):
        send_web_push(subscription, push_payload)

    return notification