from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.syllabus.models import EducationLevel


class RegistrationTests(TestCase):
    def setUp(self):
        self.level = EducationLevel.objects.create(code="BGCSE", name="Botswana General Certificate of Secondary Education")

    def test_register_creates_user_and_profile(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Kabelo",
            "last_name": "Mokgosi",
            "username": "kabelo",
            "email": "kabelo@example.com",
            "education_level": self.level.id,
            "password1": "SuperSecret123",
            "password2": "SuperSecret123",
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="kabelo")
        self.assertEqual(user.profile.education_level, self.level)

    def test_register_rejects_mismatched_passwords(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Kabelo",
            "last_name": "Mokgosi",
            "username": "kabelo2",
            "email": "kabelo2@example.com",
            "education_level": self.level.id,
            "password1": "SuperSecret123",
            "password2": "DifferentPassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="kabelo2").exists())


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student1", password="pass12345")

    def test_login_success(self):
        response = self.client.post(reverse("accounts:login"), {"username": "student1", "password": "pass12345"})
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post(reverse("accounts:login"), {"username": "student1", "password": "wrong"})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(username="student1", password="pass12345")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)


class ProtectedPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student2", password="pass12345")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username="student2", password="pass12345")
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_timetable_requires_login(self):
        response = self.client.get(reverse("timetable:timetable"))
        self.assertEqual(response.status_code, 302)

    def test_progress_requires_login(self):
        response = self.client.get(reverse("progress:my_progress"))
        self.assertEqual(response.status_code, 302)
