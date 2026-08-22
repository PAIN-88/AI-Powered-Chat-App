from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max
from .models import Group, GroupMessage


@login_required
def create_group_view(request):
    if request.method == "POST":
        name  = request.POST.get("name")
        member_ids = request.POST.getlist("members")

        if not name:
            users = User.objects.exclude(id=request.user.id)
            return render(
                request,
                'group/create_group.html', {
                    'user':users,
                    'error': 'Group name  is required.',
                }
            )
        group = Group.objects.create(name=name, owner=request.user)
        group.members.add(request.user)
        if member_ids:
            group.members.add(*member_ids)

        return redirect('group_room', group_id=group.id)

    users = User.objects.exclude(id = request.user.id)
    return render(request, 'groups/create_group.html',{'users':users})

@login_required
def group_inbox_view(request):
    groups = Group.objects.filter(members = request.user).annotate(
        last_message_time = Max('messages__timestamp')
    ).order_by('-last_message_time')
    group_data = []
    for group in groups:
        last_message = group.messages.last()
        group_data.append({
            'group': group,
            'last_message': last_message,
            'is_owner': group.owner_id == request.user.id,
        })
    return render(request, 'groups/group_inbox.html', {'group_data':group_data})
    
@login_required
def group_room_view(request, group_id):
    group = get_object_or_404(Group, id=group_id, members=request.user)
    messages = group.messages.all()
    non_members = User.objects.exclude(id__in=group.members.all())
    return render(request, 'groups/group_room.html', {
        'group': group,
        'messages': messages,
        'is_owner': group.owner_id == request.user.id,
        'non_members': non_members,
    })


@login_required
def add_group_member_view(request, group_id):
    group = get_object_or_404(Group, id= group_id, members = request.user)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user_to_add = get_object_or_404(User, id = user_id)
        group.members.add(user_to_add)

    return redirect('group_room', group_id=group_id)

@login_required
def remove_group_member_view(request, group_id, user_id):
    group = get_object_or_404(Group, id= group_id, owner = request.user)

    if request.method == 'POST':
        user_to_remove = get_object_or_404(User, id= user_id)
        if user_to_remove.id != group.owner_id:
            group.members.remove(user_to_remove)

        return redirect('group_room', group_id=group.id)

@login_required
def delete_group_view(request, group_id):
    group = get_object_or_404(Group, id=  group_id, owner = request.user)
    group.delete()
    return redirect('group_inbox')