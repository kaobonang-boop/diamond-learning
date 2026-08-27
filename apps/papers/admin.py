from django.contrib import admin
from .models import PastPaper, SolvedQuestion, TopicalQuestion, TopicalAttempt


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ("subject", "year", "paper_number", "uploaded_at")
    list_filter = ("subject__education_level", "subject", "year")


@admin.register(SolvedQuestion)
class SolvedQuestionAdmin(admin.ModelAdmin):
    list_display = ("subject", "year", "paper_number", "question_number")
    list_filter = ("subject__education_level", "subject", "year")
    search_fields = ("question_text",)


class TopicalQuestionInline(admin.TabularInline):
    model = TopicalQuestion
    extra = 1


@admin.register(TopicalQuestion)
class TopicalQuestionAdmin(admin.ModelAdmin):
    list_display = ("topic", "question_text", "correct_option")
    list_filter = ("topic__subject__education_level", "topic__subject")
    search_fields = ("question_text",)


admin.site.register(TopicalAttempt)
