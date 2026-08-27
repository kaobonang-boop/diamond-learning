from django.contrib import admin
from .models import EducationLevel, Subject, Topic, Subtopic, TopicProgress


class SubtopicInline(admin.TabularInline):
    model = Subtopic
    extra = 1


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "order")
    ordering = ("order",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "education_level")
    list_filter = ("education_level",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "order")
    list_filter = ("subject__education_level", "subject")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [SubtopicInline]


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "topic", "status", "updated_at")
    list_filter = ("status",)
