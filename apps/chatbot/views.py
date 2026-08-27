import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import ChatConversation, ChatMessage
from .providers import ChatContext, get_ai_provider


@login_required
def chat_home(request, conversation_id=None):
    conversations = ChatConversation.objects.filter(user=request.user)
    conversation = None
    if conversation_id:
        conversation = get_object_or_404(ChatConversation, pk=conversation_id, user=request.user)
    elif conversations.exists():
        conversation = conversations.first()

    return render(request, "chatbot/chat.html", {
        "conversations": conversations,
        "conversation": conversation,
        "messages": conversation.messages.all() if conversation else [],
    })


@login_required
@require_POST
def new_conversation(request):
    subject_id = request.POST.get("subject") or None
    topic_id = request.POST.get("topic") or None
    language = request.POST.get("language", "en")
    conversation = ChatConversation.objects.create(
        user=request.user, subject_id=subject_id, topic_id=topic_id, language=language,
    )
    return redirect("chatbot:chat_conversation", conversation_id=conversation.id)


@login_required
@require_POST
def send_message(request, conversation_id):
    conversation = get_object_or_404(ChatConversation, pk=conversation_id, user=request.user)
    text = request.POST.get("message", "").strip()
    if not text:
        return JsonResponse({"error": "Message can't be empty."}, status=400)

    user_msg = ChatMessage.objects.create(conversation=conversation, role="user", content=text)

    if conversation.messages.filter(role="user").count() == 1:
        conversation.title = text[:60]
        conversation.save(update_fields=["title"])

    history = [{"role": m.role if m.role == "user" else "assistant", "content": m.content}
               for m in conversation.messages.exclude(pk=user_msg.pk)]

    context = ChatContext(
        subject=conversation.subject.name if conversation.subject else None,
        topic=conversation.topic.title if conversation.topic else None,
        language=conversation.language,
        history=history,
    )
    provider = get_ai_provider()
    reply_text = provider.reply(text, context)

    assistant_msg = ChatMessage.objects.create(conversation=conversation, role="assistant", content=reply_text)

    return JsonResponse({
        "user_message": {"id": user_msg.id, "content": user_msg.content},
        "assistant_message": {"id": assistant_msg.id, "content": assistant_msg.content},
    })
