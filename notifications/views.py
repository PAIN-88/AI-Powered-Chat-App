from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

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