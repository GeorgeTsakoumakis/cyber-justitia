from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, PostVote, CommentVote
from .utils import update_views
from .forms import CreatePostForm, CreateCommentForm, PostVoteForm, CommentVoteForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def forums(request):
    vote_form = PostVoteForm()
    posts = Post.objects.filter(is_deleted=False).order_by("-created_at")
    paginator = Paginator(posts, 5)  # Show 5 posts per page

    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        "vote_form": vote_form,
        "page_obj": page_obj,
    }
    return render(request, "forum.html", context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.get_comments()
    # print comment votes
    for comment in comments:
        print(comment.votes)
    # Comment creation form
    comment_form = CreateCommentForm()
    post_vote_form = PostVoteForm()
    comment_vote_form = CommentVoteForm()
    context = {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "post_vote_form": post_vote_form,
        "comment_vote_form": comment_vote_form,
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


def create_comment(request, slug):
    # Don't 404, redirect to login
    if not request.user.is_authenticated:
        return redirect("login")
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            Comment.objects.create(user=request.user, post=post, text=comment)
            return redirect("post_detail", slug=slug)
    else:
        form = CreateCommentForm()
        return render(request, "forumpost.html", {"comment_form": form})


@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user == post.user or request.user.is_staff:
        post.delete()
    return redirect("forums")


@login_required
def delete_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.user == comment.user or request.user.is_staff:
        comment.delete()
    return redirect("post_detail", slug=slug)


@login_required
def vote_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == "POST":
        vote_form = PostVoteForm(request.POST)
        if vote_form.is_valid():
            vote_type = vote_form.cleaned_data["vote_type"]
            if vote_type == PostVote.VoteType.UPVOTE:
                post.upvote(request.user)
            elif vote_type == PostVote.VoteType.DOWNVOTE:
                post.downvote(request.user)
        else:
            # 400 Bad Request
            return render(request, "errors/400.html", status=400)
    return redirect("post_detail", slug=slug)


@login_required
def vote_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.method == "POST":
        vote_form = CommentVoteForm(request.POST)
        if vote_form.is_valid():
            vote_type = vote_form.cleaned_data["vote_type"]
            if vote_type == CommentVote.VoteType.UPVOTE:
                print("Before ", comment.votes)
                comment.upvote(request.user)
                print("After ", comment.votes)
            elif vote_type == CommentVote.VoteType.DOWNVOTE:
                print("Before ", comment.votes)
                comment.downvote(request.user)
                print("After ", comment.votes)
        else:
            # 400 Bad Request
            return render(request, "errors/400.html", status=400)
    return redirect("post_detail", slug=slug)

def search(request):
    return render(request, "search.html")
