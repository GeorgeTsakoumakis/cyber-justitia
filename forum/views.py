from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, PostVote, CommentVote
from .utils import update_views
from .forms import CreatePostForm, CreateCommentForm, PostVoteForm, CommentVoteForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.decorators import ban_forbidden


@ban_forbidden(redirect_url="/banned/")
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


@ban_forbidden(redirect_url="/banned/")
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.get_comments()
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


@ban_forbidden(redirect_url="/banned/")
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


@ban_forbidden(redirect_url="/banned/")
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
@ban_forbidden(redirect_url="/banned/")
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.user == post.user or request.user.is_staff:
        post.delete()
    return redirect("forums")


@login_required
@ban_forbidden(redirect_url="/banned/")
def delete_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.user == comment.user or request.user.is_staff:
        comment.delete()
    return redirect("post_detail", slug=slug)


@login_required
@ban_forbidden(redirect_url="/banned/")
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
@ban_forbidden(redirect_url="/banned/")
def vote_comment(request, slug, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    if request.method == "POST":
        vote_form = CommentVoteForm(request.POST)
        if vote_form.is_valid():
            vote_type = vote_form.cleaned_data["vote_type"]
            if vote_type == CommentVote.VoteType.UPVOTE:
                comment.upvote(request.user)
            elif vote_type == CommentVote.VoteType.DOWNVOTE:
                comment.downvote(request.user)
        else:
            # 400 Bad Request
            return render(request, "errors/400.html", status=400)
    return redirect("post_detail", slug=slug)


@login_required
@ban_forbidden(redirect_url="/banned/")
def search(request):
    query = request.GET.get('q')

    # Check if a query was provided
    if query:
        all_posts = Post.objects.filter(title__icontains=query).order_by('-created_at')
    else:
        all_posts = Post.objects.none()  # Return an empty queryset if no query

    paginator = Paginator(all_posts, 5)  # Show 5 posts per page.
    page_number = request.GET.get('page')

    try:
        # Get the posts for the requested page
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'search.html', {'page_obj': page_obj, 'query': query})
