from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.syllabus.models import EducationLevel, Subject, Topic
from .models import TopicalQuestion, TopicalAttempt


class TopicalQuizTests(TestCase):
    def setUp(self):
        self.level = EducationLevel.objects.create(code="BGCSE", name="BGCSE")
        self.subject = Subject.objects.create(education_level=self.level, name="Physics")
        self.topic = Topic.objects.create(subject=self.subject, title="Mechanics")
        self.q1 = TopicalQuestion.objects.create(
            topic=self.topic, question_text="Q1", option_a="a", option_b="b", option_c="c", option_d="d", correct_option="B",
        )
        self.q2 = TopicalQuestion.objects.create(
            topic=self.topic, question_text="Q2", option_a="a", option_b="b", option_c="c", option_d="d", correct_option="C",
        )
        self.user = User.objects.create_user(username="quizuser", password="pass12345")

    def test_quiz_requires_login(self):
        response = self.client.get(reverse("papers:topical_quiz", args=[self.topic.id]))
        self.assertEqual(response.status_code, 302)

    def test_quiz_scores_correctly(self):
        self.client.login(username="quizuser", password="pass12345")
        response = self.client.post(reverse("papers:topical_quiz", args=[self.topic.id]), {
            f"q{self.q1.id}": "B",  # correct
            f"q{self.q2.id}": "A",  # wrong
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Score: 1/2")
        self.assertEqual(TopicalAttempt.objects.filter(user=self.user, is_correct=True).count(), 1)
        self.assertEqual(TopicalAttempt.objects.filter(user=self.user, is_correct=False).count(), 1)

    def test_attempt_is_correct_computed_on_save(self):
        attempt = TopicalAttempt.objects.create(user=self.user, question=self.q1, selected_option="B")
        self.assertTrue(attempt.is_correct)
        attempt2 = TopicalAttempt.objects.create(user=self.user, question=self.q1, selected_option="A")
        self.assertFalse(attempt2.is_correct)
