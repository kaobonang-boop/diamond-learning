from difflib import SequenceMatcher

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from apps.notes.models import Note
from apps.papers.models import PastPaper, SolvedQuestion, TopicalQuestion
from apps.syllabus.models import Subject, Topic
from apps.timetable.models import StudySession
from apps.progress.services import dashboard_summary

# Minimum similarity (0-1) for a fuzzy match to surface — tuned so a typo
# like "bilogy" -> "Biology" still hits, without flooding results with
# unrelated words that happen to share a few letters.
FUZZY_THRESHOLD = 0.6


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


def search_suggest(request):
    """Powers the live dropdown under the search bar (Diamond Search).
    Matches subjects/topics/notes across EVERY level (a query like "digestive
    system" will show it from PSLE Science, JCE Science and BGCSE Biology
    alike, if it exists in all three) and tolerates typos ("bilogy" still
    finds "Biology") using a similarity score, not just exact substrings."""
    q = request.GET.get("q", "").strip()
    candidates = []  # (score, name, tag, url) — scored and sorted below

    if q and len(q) >= 2:
        q_lower = q.lower()

        def score(name):
            """1.0 for an exact substring hit (typed correctly), otherwise a
            fuzzy similarity ratio so small typos still surface a result."""
            name_lower = name.lower()
            if q_lower in name_lower:
                return 1.0
            return SequenceMatcher(None, q_lower, name_lower).ratio()

        for subject in Subject.objects.select_related("education_level").all():
            s = score(subject.name)
            if s >= FUZZY_THRESHOLD:
                candidates.append((s, subject.name, f"{subject.education_level.code} · Syllabus", reverse(
                    "syllabus:subject_detail", args=[subject.education_level.code.lower(), subject.slug]
                )))

        for topic in Topic.objects.select_related("subject", "subject__education_level").all():
            s = score(topic.title)
            if s >= FUZZY_THRESHOLD:
                candidates.append((s, topic.title, f"{topic.subject.name} ({topic.subject.education_level.code}) · Topic", reverse(
                    "syllabus:subject_detail", args=[topic.subject.education_level.code.lower(), topic.subject.slug]
                )))

        for note in Note.objects.select_related("topic", "topic__subject", "topic__subject__education_level").all():
            s = score(note.title)
            if s >= FUZZY_THRESHOLD:
                candidates.append((s, note.title, f"{note.topic.subject.name} ({note.topic.subject.education_level.code}) · Note", reverse(
                    "notes:note_detail", args=[note.id]
                )))

    # Highest-scoring, most-relevant matches first; de-duplicate identical (name, tag) pairs.
    seen = set()
    matches = []
    for s, name, tag, url in sorted(candidates, key=lambda c: c[0], reverse=True):
        key = (name, tag)
        if key in seen:
            continue
        seen.add(key)
        matches.append({"name": name, "tag": tag, "url": url})
        if len(matches) >= 12:
            break

    return JsonResponse({"query": q, "matches": matches, "see_all_url": f"{reverse('core:search')}?q={q}"})
