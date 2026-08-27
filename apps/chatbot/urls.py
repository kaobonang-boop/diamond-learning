from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_home, name="chat_home"),
    path("new/", views.new_conversation, name="new_conversation"),
    path("<int:conversation_id>/", views.chat_home, name="chat_conversation"),
    path("<int:conversation_id>/send/", views.send_message, name="send_message"),
]
