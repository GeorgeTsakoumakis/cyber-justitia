"""
This file contains the URL patterns for the chatbot app.

Author: Georgios Tsakoumakis
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.chatbot_home, name="chatbot_home"),
    path("process/", views.process_chat_message, name="process_chat_message"),
    path("<int:session_id>/", views.chatbot_session, name="chatbot_session"),
    path("create_session/", views.create_session, name="create_session"),
]
