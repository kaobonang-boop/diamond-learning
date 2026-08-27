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

    @property
    def display_name(self):
        full = self.user.get_full_name()
        return full if full else self.user.get_username()
