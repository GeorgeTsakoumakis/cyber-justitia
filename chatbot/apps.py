"""
This file is used to configure the app name.

Author: Georgios Tsakoumakis
"""

from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chatbot"
