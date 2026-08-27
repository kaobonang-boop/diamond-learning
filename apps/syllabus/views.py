from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.progress.services import syllabus_completion_percent
from .models import EducationLevel, Subject, Topic, TopicProgress


def level_list(request):
    levels = EducationLevel.objects.prefetch_related("subjects")
    active = request.GET.get("level", "psle")
    return render(request, "syllabus/level_list.html", {"levels": levels, "active": active})


def subject_detail(request, level_code, subject_slug):
    level = get_object_or_404(EducationLevel, code__iexact=level_code)
    subject = get_object_or_404(Subject, education_level=level, slug=subject_slug)
    topics = subject.topics.prefetch_related("subtopics")

    progress_map = {}
    if request.user.is_authenticated:
        progress_map = {
            tp.topic_id: tp.status
            for tp in TopicProgress.objects.filter(user=request.user, topic__subject=subject)
        }

    topic_rows = [
        {"topic": t, "status": progress_map.get(t.id, TopicProgress.NOT_STARTED)}
        for t in topics
    ]

    percent = syllabus_completion_percent(request.user, subject) if request.user.is_authenticated else 0

    return render(request, "syllabus/subject_detail.html", {
        "level": level, "subject": subject, "topic_rows": topic_rows, "percent": percent,
        "status_choices": TopicProgress.STATUS_CHOICES,
    })


@login_required
@require_POST
def set_topic_status(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    status = request.POST.get("status")
    valid = {c[0] for c in TopicProgress.STATUS_CHOICES}
    if status in valid:
        TopicProgress.objects.update_or_create(user=request.user, topic=topic, defaults={"status": status})
    return redirect("syllabus:subject_detail", level_code=topic.subject.education_level.code.lower(), subject_slug=topic.subject.slug)
