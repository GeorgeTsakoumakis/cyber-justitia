from django.urls import path
from . import views

urlpatterns = [
    path("", views.forums, name="forums_home"),
    path("forums", views.forums, name="forums"),
]
