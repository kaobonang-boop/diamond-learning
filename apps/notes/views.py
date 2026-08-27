from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.syllabus.models import EducationLevel, Subject, Topic
from .models import FavouriteNote, Note, NoteReadProgress


def level_list(request):
    levels = EducationLevel.objects.prefetch_related("subjects")
    return render(request, "notes/level_list.html", {"levels": levels})


def subject_notes(request, level_code, subject_slug):
    level = get_object_or_404(EducationLevel, code__iexact=level_code)
    subject = get_object_or_404(Subject, education_level=level, slug=subject_slug)

    notes = Note.objects.filter(topic__subject=subject).select_related("topic")

    q = request.GET.get("q", "").strip()
    if q:
        notes = notes.filter(Q(title__icontains=q) | Q(content__icontains=q))

    topic_slug = request.GET.get("topic", "")
    if topic_slug:
        notes = notes.filter(topic__slug=topic_slug)

    favourite_ids = set()
    if request.user.is_authenticated:
        favourite_ids = set(FavouriteNote.objects.filter(user=request.user, note__in=notes).values_list("note_id", flat=True))

    return render(request, "notes/subject_notes.html", {
        "level": level, "subject": subject, "notes": notes, "q": q,
        "topics": subject.topics.all(), "active_topic": topic_slug,
        "favourite_ids": favourite_ids,
    })


def note_detail(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    is_favourite = False
    read_progress = None
    if request.user.is_authenticated:
        is_favourite = FavouriteNote.objects.filter(user=request.user, note=note).exists()
        read_progress, _ = NoteReadProgress.objects.get_or_create(user=request.user, note=note)
        # Opening a note counts as reading at least its first section.
        if read_progress.sections_read == 0:
            read_progress.sections_read = 1
            read_progress.save()

    return render(request, "notes/note_detail.html", {
        "note": note, "is_favourite": is_favourite, "read_progress": read_progress,
    })


@login_required
@require_POST
def toggle_favourite(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    fav, created = FavouriteNote.objects.get_or_create(user=request.user, note=note)
    if not created:
        fav.delete()
    return redirect("notes:note_detail", note_id=note.id)


@login_required
@require_POST
def mark_note_progress(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    progress, _ = NoteReadProgress.objects.get_or_create(user=request.user, note=note)
    action = request.POST.get("action")
    if action == "complete":
        progress.completed = True
        progress.sections_read = note.section_count()
    elif action == "reset":
        progress.completed = False
        progress.sections_read = 0
    progress.save()
    return redirect("notes:note_detail", note_id=note.id)


@login_required
def my_favourites(request):
    favourites = FavouriteNote.objects.filter(user=request.user).select_related("note", "note__topic")
    return render(request, "notes/my_favourites.html", {"favourites": favourites})
