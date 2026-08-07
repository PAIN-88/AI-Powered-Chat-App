from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from chat.models import Conversation, Message
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
def ai_chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        AIConversation.objects.create(user = request.user, role="user", content = user_message)

        history = AIConversation.objects.filter(user = request.user).order_by("-timestamp")[:10]
        history = list(reversed(history))

        messages = [{"role": "system", "content": "You are a helpfull assistant."}]
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