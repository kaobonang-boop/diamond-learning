from django.contrib import admin
from .models import StudySession


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "date", "start_time", "end_time", "completed")
    list_filter = ("completed", "date")
