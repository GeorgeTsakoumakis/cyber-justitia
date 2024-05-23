from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .utils import update_views
from .forms import CreatePostForm


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


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            # Set the user of the post to the current user
            post.user = request.user
            post.save()
            return redirect("post_detail", slug=post.slug)
    else:
        form = CreatePostForm()
    return render(request, "postcreation.html", {"form": form})
