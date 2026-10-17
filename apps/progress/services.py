"""
Central place for computing a student's progress numbers. Keeping this in
one module means the dashboard, the syllabus pages, and the My Progress page
can never disagree about how a percentage is calculated.
"""
from django.db.models import Count, Q

from apps.syllabus.models import Subject, Topic, TopicProgress
from apps.notes.models import Note, NoteReadProgress
from apps.papers.models import TopicalQuestion, TopicalAttempt


def syllabus_completion_percent(user, subject: Subject) -> int:
    topics = Topic.objects.filter(subject=subject)
    total = topics.count()
    if not total:
        return 0
    completed = TopicProgress.objects.filter(
        user=user, topic__subject=subject, status=TopicProgress.COMPLETED
    ).count()
    return round(100 * completed / total)


def notes_completion_percent(user, subject: Subject) -> int:
    notes = Note.objects.filter(topic__subject=subject)
    total = notes.count()
    if not total:
        return 0
    completed = NoteReadProgress.objects.filter(user=user, note__topic__subject=subject, completed=True).count()
    return round(100 * completed / total)


def topical_score_percent(user, subject: Subject) -> int:
    """% of this subject's topical questions the student has answered correctly
    at least once (their best attempt counts)."""
    questions = TopicalQuestion.objects.filter(topic__subject=subject)
    total = questions.count()
    if not total:
        return 0
    correct_question_ids = set(
        TopicalAttempt.objects.filter(
            user=user, question__topic__subject=subject, is_correct=True
        ).values_list("question_id", flat=True)
    )
    return round(100 * len(correct_question_ids) / total)


def subject_breakdown(user, subject: Subject) -> dict:
    return {
        "subject": subject,
        "syllabus": syllabus_completion_percent(user, subject),
        "notes": notes_completion_percent(user, subject),
        "topical": topical_score_percent(user, subject),
    }


def level_breakdown(user, education_level) -> list[dict]:
    return [subject_breakdown(user, s) for s in Subject.objects.filter(education_level=education_level)]


def overall_percent_for_level(user, education_level) -> int:
    rows = level_breakdown(user, education_level)
    if not rows:
        return 0
    values = []
    for row in rows:
        values += [row["syllabus"], row["notes"], row["topical"]]
    return round(sum(values) / len(values)) if values else 0


def _bar(done: int, total: int) -> dict:
    return {"done": done, "total": total, "percent": round(100 * done / total) if total else 0}


def dashboard_summary(user):
    """Numbers for the three dashboard progress bars (Topics, Papers, Notes),
    totalled across the student's own subjects. A student with no subjects
    saved yet falls back to every subject at their level."""
    profile = getattr(user, "profile", None)
    level = profile.education_level if profile else None

    subjects = Subject.objects.none()
    if level:
        subjects = profile.subjects.filter(education_level=level)
        if not subjects.exists():
            subjects = Subject.objects.filter(education_level=level)

    topics_total = Topic.objects.filter(subject__in=subjects).count()
    topics_done = TopicProgress.objects.filter(
        user=user, topic__subject__in=subjects, status=TopicProgress.COMPLETED
    ).count()

    notes_total = Note.objects.filter(topic__subject__in=subjects).count()
    notes_done = NoteReadProgress.objects.filter(
        user=user, note__topic__subject__in=subjects, completed=True
    ).count()

    # "Papers" = topical paper questions, counted once the student has got
    # them right at least once (same rule as the My Progress page).
    papers_total = TopicalQuestion.objects.filter(topic__subject__in=subjects).count()
    papers_done = (
        TopicalAttempt.objects.filter(user=user, is_correct=True, question__topic__subject__in=subjects)
        .values("question_id").distinct().count()
    )

    return {
        "level": level,
        "subjects": subjects,
        "topics": _bar(topics_done, topics_total),
        "papers": _bar(papers_done, papers_total),
        "notes": _bar(notes_done, notes_total),
    }
