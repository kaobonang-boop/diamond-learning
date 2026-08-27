from rest_framework import viewsets, permissions

from .models import PastPaper, SolvedQuestion, TopicalQuestion
from .serializers import PastPaperSerializer, SolvedQuestionSerializer, TopicalQuestionSerializer


class PastPaperViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PastPaper.objects.select_related("subject", "subject__education_level").all()
    serializer_class = PastPaperSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        subject = self.request.query_params.get("subject")
        year = self.request.query_params.get("year")
        if subject:
            qs = qs.filter(subject_id=subject)
        if year:
            qs = qs.filter(year=year)
        return qs


class SolvedQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SolvedQuestion.objects.select_related("subject").all()
    serializer_class = SolvedQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TopicalQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TopicalQuestion.objects.select_related("topic").all()
    serializer_class = TopicalQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
