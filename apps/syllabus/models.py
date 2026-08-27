from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class EducationLevel(models.Model):
    """PSLE, JCE, or BGCSE."""
    code = models.CharField(max_length=10, unique=True)  # PSLE / JCE / BGCSE
    name = models.CharField(max_length=150)               # full name
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.code


class Subject(models.Model):
    education_level = models.ForeignKey(EducationLevel, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("education_level", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.education_level.code})"

    def get_absolute_url(self):
        return reverse("syllabus:subject_detail", args=[self.education_level.code.lower(), self.slug])


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    learning_objectives = models.TextField(blank=True, help_text="One objective per line.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]
        unique_together = ("subject", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.name} — {self.title}"

    def objectives_list(self):
        return [line.strip() for line in self.learning_objectives.splitlines() if line.strip()]


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title


class TopicProgress(models.Model):
    """A student's completion status for one syllabus topic (the 'StudentProgress' model from the spec)."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (NOT_STARTED, "Not Started"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
    ]

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="topic_progress")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="progress_entries")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NOT_STARTED)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "topic")
        verbose_name_plural = "Topic progress"

    def __str__(self):
        return f"{self.user} — {self.topic} — {self.status}"
