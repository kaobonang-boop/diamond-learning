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


def dashboard_summary(user):
    profile = getattr(user, "profile", None)
    level = profile.education_level if profile else None
    overall = overall_percent_for_level(user, level) if level else 0
    subjects = profile.subjects.all() if profile else Subject.objects.none()
    return {
        "level": level,
        "overall_percent": overall,
        "subjects": subjects,
        "questions_answered": TopicalAttempt.objects.filter(user=user).count(),
        "notes_completed": NoteReadProgress.objects.filter(user=user, completed=True).count(),
        "topics_completed": TopicProgress.objects.filter(user=user, status=TopicProgress.COMPLETED).count(),
    }
