from django.conf import settings
from django.db import models

from apps.syllabus.models import Topic


class Note(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Supports basic markdown-style paragraphs.")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_notes")
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["topic__order", "title"]

    def __str__(self):
        return self.title

    @property
    def subject(self):
        return self.topic.subject

    @property
    def education_level(self):
        return self.topic.subject.education_level

    def section_count(self):
        """Rough count of readable sections, used to track reading progress."""
        return max(1, len([p for p in self.content.split("\n\n") if p.strip()]))


class FavouriteNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favourite_notes")
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="favourited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "note")


class NoteReadProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="note_progress")
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name="read_progress")
    sections_read = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    last_position = models.PositiveIntegerField(default=0, help_text="Character offset to resume reading at.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "note")

    def percent(self):
        total = self.note.section_count()
        return round(100 * min(self.sections_read, total) / total) if total else 0
