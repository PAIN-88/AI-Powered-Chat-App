from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Conversation, Message
from django.db.models import Max

def get_or_create_conversation(user1, user2):
    conversations = Conversation.objects.filter(participants = user1).filter(participants=user2)
    conversation = conversations.first()
    if conversation:
        return conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(user1,user2)
    return conversation

@login_required
def user_list_view(request):
    users = User.objects.exclude(id = request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

@login_required
def start_chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    conversation = get_or_create_conversation(request.user, other_user)
    return redirect('chat_room', conversation_id = conversation.id)

@login_required
def inbox_view(request):
    conversations = Conversation.objects.filter(participants = request.user).annotate(
        last_message_time =Max('messages__timestamp')
    ).order_by('-last_message_time')

    conversation_data = []
    for conv in conversations:
        other_user = conv.participants.exclude(id=request.user.id).first()
        last_message = conv.messages.last()
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
        })
    return render(request, 'chat/inbox.html', {'conversation_data':conversation_data})
   
@login_required
def chat_room_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id = conversation_id, participants=request.user)
    other_user = conversation.participants.exclude(id=request.user.id).first()
    messages = conversation.messages.all()
    return render(request, 'chat/chat_room.html',{
         'conversation': conversation,
        'other_user': other_user,
        'messages': messages,
    })

@login_required
def delete_chat_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    conversation.delete()
    return redirect('inbox')
