"""
This file is used to configure the app name for the users app.

Author: Georgios Tsakoumakis
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
