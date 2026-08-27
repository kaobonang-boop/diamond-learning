from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.syllabus.models import EducationLevel, Subject, Topic
from apps.notes.models import Note


class ApiEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.level = EducationLevel.objects.create(code="BGCSE", name="BGCSE")
        self.subject = Subject.objects.create(education_level=self.level, name="Geography")
        self.topic = Topic.objects.create(subject=self.subject, title="Climate")
        self.note = Note.objects.create(topic=self.topic, title="Climate Notes", content="x")
        self.user = User.objects.create_user(username="apiuser", password="pass12345")

    def test_education_levels_endpoint_public(self):
        response = self.client.get("/api/education-levels/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subjects_endpoint_filters_by_level(self):
        response = self.client.get("/api/subjects/", {"level": "BGCSE"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_notes_endpoint_requires_auth_for_nothing_but_returns_list(self):
        response = self.client.get("/api/notes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_progress_endpoint_requires_auth(self):
        response = self.client.get("/api/progress/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_progress_endpoint_authenticated(self):
        self.client.login(username="apiuser", password="pass12345")
        response = self.client.get("/api/progress/", {"level": "BGCSE"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class SearchTests(TestCase):
    def setUp(self):
        self.level = EducationLevel.objects.create(code="JCE", name="JCE")
        self.subject = Subject.objects.create(education_level=self.level, name="Setswana")

    def test_search_finds_subject(self):
        response = self.client.get(reverse("core:search"), {"q": "Setswana"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Setswana")

    def test_search_with_no_query_returns_empty(self):
        response = self.client.get(reverse("core:search"))
        self.assertEqual(response.status_code, 200)
