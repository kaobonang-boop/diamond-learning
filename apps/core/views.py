from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from apps.notes.models import Note
from apps.papers.models import PastPaper, SolvedQuestion, TopicalQuestion
from apps.syllabus.models import Subject, Topic
from apps.timetable.models import StudySession
from apps.progress.services import dashboard_summary


def home(request):
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    summary = dashboard_summary(request.user)
    upcoming_sessions = StudySession.objects.filter(user=request.user, completed=False).order_by("date", "start_time")[:5]
    recent_notes = Note.objects.filter(
        topic__subject__education_level=summary["level"]
    ).order_by("-last_updated")[:4] if summary["level"] else Note.objects.none()

    context = {
        **summary,
        "upcoming_sessions": upcoming_sessions,
        "recent_notes": recent_notes,
    }
    return render(request, "core/dashboard.html", context)


def search(request):
    q = request.GET.get("q", "").strip()
    results = {"subjects": [], "topics": [], "notes": [], "past_papers": [], "solved_questions": [], "topical_questions": []}
    if q:
        results["subjects"] = Subject.objects.filter(name__icontains=q).select_related("education_level")[:8]
        results["topics"] = Topic.objects.filter(title__icontains=q).select_related("subject")[:8]
        results["notes"] = Note.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).select_related("topic")[:8]
        results["past_papers"] = PastPaper.objects.filter(subject__name__icontains=q).select_related("subject")[:8]
        results["solved_questions"] = SolvedQuestion.objects.filter(question_text__icontains=q).select_related("subject")[:8]
        results["topical_questions"] = TopicalQuestion.objects.filter(question_text__icontains=q).select_related("topic")[:8]
    return render(request, "core/search_results.html", {"q": q, "results": results})
