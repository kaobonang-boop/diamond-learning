from django.urls import path
from . import views

app_name = "papers"

urlpatterns = [
    path("past/", views.past_papers_home, name="past_papers_home"),
    path("past/download/<int:paper_id>/", views.download_past_paper, name="download_past_paper"),
    path("past/<str:level_code>/<slug:subject_slug>/", views.past_papers_subject, name="past_papers_subject"),

    path("solved/", views.solved_papers_home, name="solved_papers_home"),
    path("solved/<str:level_code>/<slug:subject_slug>/", views.solved_papers_subject, name="solved_papers_subject"),

    path("topical/", views.topical_home, name="topical_home"),
    path("topical/quiz/<int:topic_id>/", views.topical_quiz, name="topical_quiz"),
    path("topical/<str:level_code>/<slug:subject_slug>/", views.topical_subject, name="topical_subject"),
]
