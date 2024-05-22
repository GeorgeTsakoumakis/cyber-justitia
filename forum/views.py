from django.shortcuts import render, get_object_or_404
from .models import Post
from .utils import update_views


def forums(request):
    posts = Post.objects.all()

    context = {
        "posts": posts,
    }
    return render(request, "forum.html", context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    context = {
        "post": post,
    }
    update_views(request, post)

    return render(request, "forumpost.html", context)
