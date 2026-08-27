from django.conf import settings
from django.db import models

from apps.syllabus.models import EducationLevel, Subject, Topic


class PastPaper(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="past_papers")
    year = models.PositiveSmallIntegerField()
    paper_number = models.CharField(max_length=50, help_text="e.g. 'Paper 1', 'Practical (Paper 2)'")
    file = models.FileField(upload_to="past_papers/", blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_papers")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "paper_number"]
        unique_together = ("subject", "year", "paper_number")

    @property
    def education_level(self):
        return self.subject.education_level

    def __str__(self):
        return f"{self.subject.name} — {self.paper_number} ({self.year})"


class SolvedQuestion(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="solved_questions")
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="solved_questions")
    year = models.PositiveSmallIntegerField()
    paper_number = models.CharField(max_length=50)
    question_number = models.CharField(max_length=20)
    question_text = models.TextField()
    step_by_step_explanation = models.TextField()
    final_answer = models.TextField()

    class Meta:
        ordering = ["-year", "paper_number", "question_number"]

    @property
    def education_level(self):
        return self.subject.education_level

    def __str__(self):
        return f"{self.subject.name} {self.paper_number} Q{self.question_number} ({self.year})"


class TopicalQuestion(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topical_questions")
    question_text = models.TextField()
    option_a = models.CharField(max_length=300)
    option_b = models.CharField(max_length=300)
    option_c = models.CharField(max_length=300)
    option_d = models.CharField(max_length=300)
    CORRECT_CHOICES = [("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    correct_option = models.CharField(max_length=1, choices=CORRECT_CHOICES)
    explanation = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.topic} — Q{self.pk}"

    def options(self):
        return [("A", self.option_a), ("B", self.option_b), ("C", self.option_c), ("D", self.option_d)]


class TopicalAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="topical_attempts")
    question = models.ForeignKey(TopicalQuestion, on_delete=models.CASCADE, related_name="attempts")
    selected_option = models.CharField(max_length=1, choices=TopicalQuestion.CORRECT_CHOICES)
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_option == self.question.correct_option
        super().save(*args, **kwargs)
