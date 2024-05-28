from django.urls import path
from . import views

urlpatterns = [
    path("", views.forums, name="forums"),
    path("post/<slug>/", views.post_detail, name="post_detail"),
    path("create_post/", views.create_post, name="create_post"),
    path("create_comment/<slug>/", views.create_comment, name="create_comment"),
    path("delete_post/<slug>/", views.delete_post, name="delete_post"),
    path("vote_post/<slug>/", views.vote_post, name="vote_post"),
    path(
        "vote_comment/<slug>/<int:comment_id>/", views.vote_comment, name="vote_comment"
    ),
    path(
        "delete_comment/<slug>/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
]
