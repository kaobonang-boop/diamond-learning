from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.syllabus.models import EducationLevel, Subject, Topic
from .models import Note, FavouriteNote, NoteReadProgress


class NoteTests(TestCase):
    def setUp(self):
        self.level = EducationLevel.objects.create(code="PSLE", name="PSLE")
        self.subject = Subject.objects.create(education_level=self.level, name="English")
        self.topic = Topic.objects.create(subject=self.subject, title="Comprehension")
        self.note = Note.objects.create(topic=self.topic, title="Comprehension Notes", content="Para one.\n\nPara two.\n\nPara three.")
        self.user = User.objects.create_user(username="reader", password="pass12345")

    def test_note_section_count(self):
        self.assertEqual(self.note.section_count(), 3)

    def test_favourite_toggle_requires_login(self):
        response = self.client.post(reverse("notes:toggle_favourite", args=[self.note.id]))
        self.assertEqual(response.status_code, 302)

    def test_favourite_toggle_creates_and_removes(self):
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("notes:toggle_favourite", args=[self.note.id]))
        self.assertTrue(FavouriteNote.objects.filter(user=self.user, note=self.note).exists())
        self.client.post(reverse("notes:toggle_favourite", args=[self.note.id]))
        self.assertFalse(FavouriteNote.objects.filter(user=self.user, note=self.note).exists())

    def test_mark_note_complete(self):
        self.client.login(username="reader", password="pass12345")
        self.client.post(reverse("notes:mark_note_progress", args=[self.note.id]), {"action": "complete"})
        progress = NoteReadProgress.objects.get(user=self.user, note=self.note)
        self.assertTrue(progress.completed)
        self.assertEqual(progress.percent(), 100)
