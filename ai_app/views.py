from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from chat.models import Conversation, Message
from groups.models import Group, GroupMessage
import json
from django.views.decorators.csrf import csrf_exempt
from .models import AIConversation
from .groq_utils import get_ai_reply ,call_groq_summarize

@login_required
def summarize_chat(request, conversation_id):
    conversation = Conversation.objects.filter(
        id = conversation_id,
        participants = request.user
    ).first()

    if not conversation:
        return JsonResponse({"error":"Not Found"})
    
    date = request.GET.get("date")
    messages = conversation.messages.filter(timestamp__date = date)

    if not messages.exists():
        return JsonResponse({"summary": "No message is available on this Date"})

    char_text = "\n".join([f"{m.sender.username}: {m.content}" for m in messages])

    summary = call_groq_summarize(char_text)

    return JsonResponse({"summary": summary})

@login_required
def summary_page_view(request, conversation_id):
    from chat.models import Conversation
    conversation = Conversation.objects.filter(
        id = conversation_id,
        participants = request.user
    ).first()
    if not conversation:
        return redirect('inbox')
    return render(request, 'ai_app/summary.html', {'conversation': conversation})


@login_required
def summarize_group_chat(request, group_id):
    group = Group.objects.filter(
        id = group_id,
        members = request.user
    ).first()

    if not group:
        return JsonResponse({"error": "Not Found"})

    date = request.GET.get("date")
    messages = group.messages.filter(timestamp__date = date)

    if not messages.exists():
        return JsonResponse({"summary": "No message is available on this Date"})

    char_text = "\n".join([f"{m.sender.username}: {m.content}" for m in messages])

    summary = call_groq_summarize(char_text)

    return JsonResponse({"summary": summary})


@login_required
def group_summary_page_view(request, group_id):
    group = Group.objects.filter(
        id = group_id,
        members = request.user
    ).first()
    if not group:
        return redirect('group_inbox')
    return render(request, 'ai_app/group_summary.html', {'group': group})

@login_required
def group_summary_chat_view(request, group_id):
    group = Group.objects.filter(
        id = group_id,
        members = request.user
    ).first()

    if not group:
        return JsonResponse({"error": "Not Found"})

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    data = json.loads(request.body)
    date = data.get("date")
    user_message = data.get("message")
    client_history = data.get("history", [])

    if not date:
        return JsonResponse({"error": "Date is required"})

    day_messages = group.messages.filter(timestamp__date=date)

    if not day_messages.exists():
        return JsonResponse({"reply": "No messages are available for this date."})

    char_text = "\n".join([f"{m.sender.username}: {m.content}" for m in day_messages])

    system_prompt = (
        f"You are an assistant helping summarize and answer questions about a group chat "
        f"named '{group.name}' for the date {date}. "
        f"Only use the following chat log as your source of truth - do not make up information "
        f"that isn't in it. If asked something the log doesn't cover, say you don't have that information.\n\n"
        f"Chat log:\n{char_text}"
    )

    messages = [{"role": "system", "content": system_prompt}]

    for h in client_history:
        role = h.get("role")
        content = h.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    reply = get_ai_reply(messages)

    return JsonResponse({"reply": reply})

@login_required
def ai_chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        AIConversation.objects.create(user = request.user, role="user", content = user_message)

        history = AIConversation.objects.filter(user = request.user).order_by("-timestamp")[:10]
        history = list(reversed(history))

        messages = [{"role": "system", "content": "You are PAIN, a helpful AI assistant integrated into the PAIN chat application. If anyone asks who you are, what your name is, or what you're called, always respond exactly with 'I am PAIN'. Keep your responses helpful, concise, and friendly."}]
        for h in history:
            role = "user" if h.role == "user" else "assistant"
            messages.append({"role": role, "content": h.content})

        ai_reply = get_ai_reply(messages)

        AIConversation.objects.create(user=request.user, role="ai", content=ai_reply)

        return JsonResponse({"reply":ai_reply})

@login_required
def ai_chat_page(request):
    history = AIConversation.objects.filter(user=request.user)
    return render(request, 'ai_app/ai_chat.html', {'history': history})