from django.urls import path
from . import views

app_name = "progress"

urlpatterns = [
    path("", views.my_progress, name="my_progress"),
]
