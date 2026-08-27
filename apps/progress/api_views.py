from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.syllabus.models import Subject
from .services import subject_breakdown


class ProgressView(APIView):
    """GET /api/progress/?level=BGCSE — this student's progress across every subject at that level."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        level_code = request.query_params.get("level")
        subjects = Subject.objects.all()
        if level_code:
            subjects = subjects.filter(education_level__code__iexact=level_code)
        else:
            profile = getattr(request.user, "profile", None)
            if profile and profile.subjects.exists():
                subjects = profile.subjects.all()

        data = [subject_breakdown(request.user, s) for s in subjects]
        for row in data:
            row["subject"] = str(row["subject"])
        return Response(data)
