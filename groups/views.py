from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Group, GroupMessage
from notifications.utils import send_notification
from ai_app.groq_utils import get_ai_reply

@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        member_ids = request.POST.getlist("members")

        if not name:
            users = User.objects.exclude(id=request.user.id)
            return render(request, 'groups/create_group.html', {
                'users': users,
                'error': 'Group name is required.',
            })

        group = Group.objects.create(name=name, owner=request.user)
        group.members.add(request.user)
        if member_ids:
            group.members.add(*member_ids)
            for uid in member_ids:
                added_user = User.objects.filter(id=uid).first()
                if added_user:
                    send_notification(
                        recipient=added_user,
                        notification_type="group_add",
                        text=f"{request.user.username} added you to '{group.name}'",
                        link=f"/groups/room/{group.id}/",
                        sender=request.user,
                    )

        return redirect('group_room', group_id=group.id)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'groups/create_group.html', {'users': users})


@login_required
def group_inbox_view(request):
    groups = Group.objects.filter(members=request.user).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    group_data = []
    for group in groups:
        last_message = group.messages.last()
        group_data.append({
            'group': group,
            'last_message': last_message,
            'is_owner': group.owner_id == request.user.id,
        })
    return render(request, 'groups/group_inbox.html', {'group_data': group_data})


@login_required
def group_room_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    messages = group.messages.filter(is_unlocked=True)
    non_members = User.objects.exclude(id__in=group.members.all())
    return render(request, 'groups/group_room.html', {
        'group': group,
        'messages': messages,
        'is_owner': group.owner_id == request.user.id,
        'non_members': non_members,
    })


@login_required
def add_group_member_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user_to_add = get_object_or_404(User, id=user_id)
        group.members.add(user_to_add)
        send_notification(
            recipient=user_to_add,
            notification_type="group_add",
            text=f"{request.user.username} added you to '{group.name}'",
            link=f"/groups/room/{group.id}/",
            sender=request.user,
        )

    return redirect('group_room', group_id=group.id)


@login_required
def remove_group_member_view(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)

    if request.method == "POST":
        user_to_remove = get_object_or_404(User, id=user_id)
        if user_to_remove.id != group.owner_id:
            group.members.remove(user_to_remove)
            send_notification(
                recipient=user_to_remove,
                notification_type="group_remove",
                text=f"{request.user.username} removed you from '{group.name}'",
                link="/groups/inbox/",
                sender=request.user,
            )

    return redirect('group_room', group_id=group.id)


@login_required
def delete_group_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, owner=request.user)

    members_to_notify = list(group.members.exclude(id=request.user.id))
    group_name = group.name

    group.delete()

    for member in members_to_notify:
        send_notification(
            recipient=member,
            notification_type="group_delete",
            text=f"{request.user.username} deleted the group '{group_name}'",
            link="/groups/inbox/",
            sender=request.user,
        )

    return redirect('group_inbox')

@login_required
def generate_icebreaker_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    messages = [
        {
            "role": "system",
            "content": "You generate short, fun icebreaker questions for group chats. "
                       "Reply with ONLY one casual, friendly icebreaker question. "
                       "No preamble, no quotes, no explanation."
        },
        {
            "role": "user",
            "content": f"Generate a fun icebreaker question for a group chat named '{group.name}'."
        },
    ]
    icebreaker_text = get_ai_reply(messages)

    GroupMessage.objects.create(
        group=group,
        sender=request.user,
        content=icebreaker_text,
        is_system_message=True,
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"group_{group.id}",
        {
            "type": "chat_message",
            "message": icebreaker_text,
            "sender": "✨ Icebreaker",
            "is_system": True,
        }
    )

    return JsonResponse({"status": "ok", "message": icebreaker_text})