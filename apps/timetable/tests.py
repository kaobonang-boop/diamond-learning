from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.syllabus.models import EducationLevel, Subject
from .models import StudySession


class StudySessionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="planner", password="pass12345")
        self.level = EducationLevel.objects.create(code="BGCSE", name="BGCSE")
        self.subject = Subject.objects.create(education_level=self.level, name="Biology")
        self.user.profile.subjects.set([self.subject])

    def test_add_session_requires_login(self):
        response = self.client.get(reverse("timetable:add_session"))
        self.assertEqual(response.status_code, 302)

    def test_add_session(self):
        self.client.login(username="planner", password="pass12345")
        response = self.client.post(reverse("timetable:add_session"), {
            "subject": self.subject.id, "topic": "", "date": "2026-09-01",
            "start_time": "14:00", "end_time": "15:00", "notes": "Revise cells",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StudySession.objects.filter(user=self.user).count(), 1)

    def test_delete_session_only_own(self):
        other = User.objects.create_user(username="other", password="pass12345")
        session = StudySession.objects.create(
            user=other, subject=self.subject, date="2026-09-01", start_time="10:00", end_time="11:00"
        )
        self.client.login(username="planner", password="pass12345")
        response = self.client.post(reverse("timetable:delete_session", args=[session.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(StudySession.objects.filter(id=session.id).exists())
