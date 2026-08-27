from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChatConversation
from .providers import ChatContext, get_ai_provider
from .serializers import ChatConversationSerializer


class ChatConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ChatConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatConversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        conversation = self.get_object()
        text = request.data.get("message", "").strip()
        if not text:
            return Response({"error": "Message can't be empty."}, status=400)

        from .models import ChatMessage
        user_msg = ChatMessage.objects.create(conversation=conversation, role="user", content=text)

        history = [{"role": m.role, "content": m.content} for m in conversation.messages.exclude(pk=user_msg.pk)]
        context = ChatContext(
            subject=conversation.subject.name if conversation.subject else None,
            topic=conversation.topic.title if conversation.topic else None,
            language=conversation.language,
            history=history,
        )
        reply_text = get_ai_provider().reply(text, context)
        assistant_msg = ChatMessage.objects.create(conversation=conversation, role="assistant", content=reply_text)

        return Response({
            "user_message": {"id": user_msg.id, "content": user_msg.content},
            "assistant_message": {"id": assistant_msg.id, "content": assistant_msg.content},
        })
