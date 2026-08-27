from django.urls import path
from . import views

app_name = "syllabus"

urlpatterns = [
    path("", views.level_list, name="level_list"),
    path("<str:level_code>/<slug:subject_slug>/", views.subject_detail, name="subject_detail"),
    path("topic/<int:topic_id>/status/", views.set_topic_status, name="set_topic_status"),
]
