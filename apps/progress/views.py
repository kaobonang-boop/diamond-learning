from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.syllabus.models import EducationLevel
from apps.papers.models import TopicalAttempt
from apps.notes.models import NoteReadProgress
from apps.syllabus.models import TopicProgress
from apps.timetable.models import StudySession
from .services import level_breakdown, overall_percent_for_level


@login_required
def my_progress(request):
    levels = EducationLevel.objects.all()
    profile = getattr(request.user, "profile", None)
    active_code = request.GET.get("level", profile.education_level.code.lower() if profile and profile.education_level else "psle")
    active_level = levels.filter(code__iexact=active_code).first() or levels.first()

    breakdown = level_breakdown(request.user, active_level) if active_level else []
    overall = overall_percent_for_level(request.user, active_level) if active_level else 0

    stats = {
        "questions_answered": TopicalAttempt.objects.filter(user=request.user).count(),
        "correct_answers": TopicalAttempt.objects.filter(user=request.user, is_correct=True).count(),
        "notes_completed": NoteReadProgress.objects.filter(user=request.user, completed=True).count(),
        "topics_completed": TopicProgress.objects.filter(user=request.user, status=TopicProgress.COMPLETED).count(),
        "study_sessions": StudySession.objects.filter(user=request.user).count(),
    }

    return render(request, "progress/my_progress.html", {
        "levels": levels, "active_level": active_level, "breakdown": breakdown,
        "overall": overall, "stats": stats,
    })
