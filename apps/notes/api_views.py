from rest_framework import viewsets, permissions

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Note.objects.select_related("topic", "topic__subject").all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        subject = self.request.query_params.get("subject")
        topic = self.request.query_params.get("topic")
        q = self.request.query_params.get("q")
        if subject:
            qs = qs.filter(topic__subject_id=subject)
        if topic:
            qs = qs.filter(topic_id=topic)
        if q:
            qs = qs.filter(title__icontains=q)
        return qs
