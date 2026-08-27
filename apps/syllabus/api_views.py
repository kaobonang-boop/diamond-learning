from rest_framework import viewsets, permissions

from .models import EducationLevel, Subject, Topic
from .serializers import EducationLevelSerializer, SubjectSerializer, TopicSerializer


class EducationLevelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer
    permission_classes = [permissions.AllowAny]


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.select_related("education_level").all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ["education_level__code"]

    def get_queryset(self):
        qs = super().get_queryset()
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(education_level__code__iexact=level)
        return qs


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.select_related("subject").all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        subject = self.request.query_params.get("subject")
        if subject:
            qs = qs.filter(subject_id=subject)
        return qs
