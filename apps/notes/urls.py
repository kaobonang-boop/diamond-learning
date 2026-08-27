from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path("", views.level_list, name="level_list"),
    path("favourites/", views.my_favourites, name="my_favourites"),
    path("note/<int:note_id>/", views.note_detail, name="note_detail"),
    path("note/<int:note_id>/favourite/", views.toggle_favourite, name="toggle_favourite"),
    path("note/<int:note_id>/progress/", views.mark_note_progress, name="mark_note_progress"),
    path("<str:level_code>/<slug:subject_slug>/", views.subject_notes, name="subject_notes"),
]
