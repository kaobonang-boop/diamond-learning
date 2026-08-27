from django.urls import path
from . import views

app_name = "timetable"

urlpatterns = [
    path("", views.timetable_view, name="timetable"),
    path("add/", views.add_session, name="add_session"),
    path("<int:session_id>/edit/", views.edit_session, name="edit_session"),
    path("<int:session_id>/delete/", views.delete_session, name="delete_session"),
    path("<int:session_id>/complete/", views.complete_session, name="complete_session"),
]
