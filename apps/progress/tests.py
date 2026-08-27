from django.contrib.auth.models import User
from django.test import TestCase

from apps.syllabus.models import EducationLevel, Subject, Topic, TopicProgress
from apps.notes.models import Note, NoteReadProgress
from apps.papers.models import TopicalQuestion, TopicalAttempt
from .services import syllabus_completion_percent, notes_completion_percent, topical_score_percent


class ProgressCalculationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="progressuser", password="pass12345")
        self.level = EducationLevel.objects.create(code="BGCSE", name="BGCSE")
        self.subject = Subject.objects.create(education_level=self.level, name="Chemistry")
        self.topic1 = Topic.objects.create(subject=self.subject, title="Atoms")
        self.topic2 = Topic.objects.create(subject=self.subject, title="Bonding")

    def test_syllabus_completion_percent_zero_when_no_progress(self):
        self.assertEqual(syllabus_completion_percent(self.user, self.subject), 0)

    def test_syllabus_completion_percent_half(self):
        TopicProgress.objects.create(user=self.user, topic=self.topic1, status=TopicProgress.COMPLETED)
        self.assertEqual(syllabus_completion_percent(self.user, self.subject), 50)

    def test_syllabus_completion_percent_full(self):
        TopicProgress.objects.create(user=self.user, topic=self.topic1, status=TopicProgress.COMPLETED)
        TopicProgress.objects.create(user=self.user, topic=self.topic2, status=TopicProgress.COMPLETED)
        self.assertEqual(syllabus_completion_percent(self.user, self.subject), 100)

    def test_notes_completion_percent(self):
        note = Note.objects.create(topic=self.topic1, title="Atoms Notes", content="x")
        NoteReadProgress.objects.create(user=self.user, note=note, completed=True)
        self.assertEqual(notes_completion_percent(self.user, self.subject), 100)

    def test_topical_score_percent_counts_best_attempt(self):
        q = TopicalQuestion.objects.create(
            topic=self.topic1, question_text="Q", option_a="a", option_b="b", option_c="c", option_d="d", correct_option="A"
        )
        TopicalAttempt.objects.create(user=self.user, question=q, selected_option="B")  # wrong first try
        TopicalAttempt.objects.create(user=self.user, question=q, selected_option="A")  # correct second try
        self.assertEqual(topical_score_percent(self.user, self.subject), 100)
