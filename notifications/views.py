from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, PushSubscription
import json
from django.views.decorators.http import require_POST

@login_required
@require_POST
def save_push_subscription_view(request):
    data = json.loads(request.body)
    endpoint = data.get("endpoint")
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")
    if endpoint and p256dh and auth:
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={"user": request.user, "p256dh": p256dh, "auth": auth},
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

@login_required
def notification_list_view(request):
    notifications = Notification.objects.filter(recipient=request.user)[:20]
    data = [
        {
        "id": n.id,
        "notification_type": n.notification_type,
        "text": n.text,
        "link": n.link,
        "is_read": n.is_read,
        "created_at": n.created_at.strftime("%b %d, %I:%M %p"),
        }
        for n in notifications
    ]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({"notifications": data, "unread_count": unread_count})

@login_required
def mark_notification_read_view(request, notification_id):
    notification = get_object_or_404(Notification, id= notification_id, recipient= request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({"success":True})

@login_required
def mark_all_read_view(request):
    Notification.objects.filter(recipient=request.user, is_read = False).update(is_read = True)
    return JsonResponse({"success":True})