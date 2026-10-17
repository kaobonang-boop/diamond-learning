from django.conf import settings
from django.db import models

from apps.syllabus.models import EducationLevel, Subject


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    education_level = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    subjects = models.ManyToManyField(Subject, blank=True, related_name="students")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.get_username()}"

    def apply_level(self, level):
        """Set the student's level and reset their subjects to that level's
        compulsory ones. Optional subjects are chosen afterwards."""
        self.education_level = level
        self.save(update_fields=["education_level"])
        self.subjects.set(level.core_subjects() if level else [])

    def set_optional_subjects(self, optional_subjects):
        """Keep the compulsory subjects for the current level and swap the
        optional ones for exactly the ones given."""
        if not self.education_level:
            return
        self.subjects.set(list(self.education_level.core_subjects()) + list(optional_subjects))

    @property
    def display_name(self):
        full = self.user.get_full_name()
        return full if full else self.user.get_username()
