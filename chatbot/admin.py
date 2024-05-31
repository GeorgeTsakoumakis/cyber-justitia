"""
This file is used to register the models in the Django admin panel.

Author: Georgios Tsakoumakis
"""

from django.contrib import admin
from .models import Message, Session

admin.site.register(Message)
admin.site.register(Session)
