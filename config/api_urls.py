"""
Diamond Learning API structure
===============================

Browsable root:      /api/
Auth:                Session auth (log in via /accounts/login/, DRF respects the session)

Endpoints:
    /api/education-levels/         GET
    /api/subjects/                 GET   ?level=BGCSE
    /api/topics/                   GET   ?subject=<id>
    /api/notes/                    GET   ?subject=<id>&topic=<id>&q=<text>
    /api/past-papers/              GET   ?subject=<id>&year=<yyyy>
    /api/solved-questions/         GET
    /api/topical-questions/        GET
    /api/progress/                 GET   ?level=BGCSE   (current student's completion %)
    /api/chat/conversations/       GET, POST
    /api/chat/conversations/<id>/  GET, PUT, DELETE
    /api/chat/conversations/<id>/send/   POST  {"message": "..."}
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.syllabus.api_views import EducationLevelViewSet, SubjectViewSet, TopicViewSet
from apps.notes.api_views import NoteViewSet
from apps.papers.api_views import PastPaperViewSet, SolvedQuestionViewSet, TopicalQuestionViewSet
from apps.progress.api_views import ProgressView
from apps.chatbot.api_views import ChatConversationViewSet

router = DefaultRouter()
router.register("education-levels", EducationLevelViewSet, basename="education-level")
router.register("subjects", SubjectViewSet, basename="subject")
router.register("topics", TopicViewSet, basename="topic")
router.register("notes", NoteViewSet, basename="note")
router.register("past-papers", PastPaperViewSet, basename="past-paper")
router.register("solved-questions", SolvedQuestionViewSet, basename="solved-question")
router.register("topical-questions", TopicalQuestionViewSet, basename="topical-question")
router.register("chat/conversations", ChatConversationViewSet, basename="chat-conversation")

urlpatterns = [
    path("progress/", ProgressView.as_view(), name="api-progress"),
    path("", include(router.urls)),
]
