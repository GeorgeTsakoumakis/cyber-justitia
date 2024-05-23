from django.urls import path
from . import views

urlpatterns = [
    path("", views.forums, name="forums"),
    path("post/<slug>/", views.post_detail, name="post_detail"),
    path("create_post/", views.create_post, name="create_post")
]
