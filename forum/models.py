"""
This module contains the models for the forum app. The models are as follows:
1. Post: Represents a post in the forum. It has a title, text, user, created_at, and is_deleted fields.
2. Comment: Represents a comment on a post. It has a post, user, text, created_at, and is_deleted fields.
3. Vote: Abstract model representing a vote. It has a user and vote_type field.
4. PostVote: Represents a vote on a post. It has a post field.
5. CommentVote: Represents a vote on a comment. It has a comment field.

Author: Georgios Tsakoumakis, Ionut-Valeriu Facaeru
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from hitcount.models import HitCount
from django.contrib.contenttypes.fields import GenericRelation
from django.shortcuts import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

CustomUser = get_user_model()


class Post(models.Model):
    """
    Post model representing a post in the forum.
    Fields:
    - post_id: Primary key of the post
    - title: Title of the post
    - slug: Slug of the post, generated from the title
    - text: Text of the post
    - user: User who created the post (foreign key to CustomUser)
    - created_at: Date and time the post was created
    - is_deleted: Boolean field indicating if the post is deleted
    - hit_count_generic: Generic relation to the HitCount model for tracking post views
    """
    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        db_table = "posts"

    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True, blank=True)
    text = models.TextField(max_length=40000)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(
        HitCount,
        object_id_field="object_pk",
        related_query_name="hit_count_generic_relation",
    )

    @property
    def votes(self):
        """
        Calculate the total votes of the post
        :return: int representing the total votes
        """
        return self.get_upvotes() - self.get_downvotes()

    def save(self, *args, **kwargs):
        """
        Save the post and perform validation checks before saving. If the slug is not set, generate it from the title.
        """
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure the slug is unique
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = (
                    slugify(self.title)
                    + "-"
                    + str(Post.objects.filter(slug=self.slug).count())
                )
        self.full_clean()
        super(Post, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Mark the post as deleted and save it. The title and text are replaced with [deleted]
        :param using: Database alias
        :param keep_parents: Whether to delete the parent objects
        :return: Post object
        """
        self.text = "[deleted]"
        self.title = "[deleted]"
        self.is_deleted = True
        self.save()
        return self

    def __str__(self):
        """
        String representation of the post
        :return: Title of the post
        """
        return self.title

    def get_url(self):
        """
        Get the URL of the post
        :return: URL of the post
        """
        return reverse("post_detail", kwargs={"slug": self.slug})

    def get_comments(self):
        """
        Get all comments for this post in descending order of creation
        :return:  QuerySet of Comment objects
        """
        return (
            Comment.objects.filter(post=self)
            .filter(is_deleted=False)
            .order_by("-created_at")
        )

    def clean(self):
        """
        Perform validation checks on the post before saving
        :raises ValidationError: If the title or text fields are empty or exceed the maximum length
        :raises ValidationError: If the title exceeds the maximum length
        :raises ValidationError: If the text exceeds the maximum length
        :return: cleaned_data
        """
        cleaned_data = super().clean()
        if not self.title:
            raise ValidationError(_("Title field is required."), code="invalid")
        if len(self.title) > 256:
            raise ValidationError(
                _("Title cannot exceed 256 characters."), code="invalid"
            )
        if not self.text:
            raise ValidationError(_("Text field is required."), code="invalid")
        if len(self.text) > 40000:
            raise ValidationError(
                _("Text cannot exceed 40000 characters."), code="invalid"
            )
        return cleaned_data

    def upvote(self, user):
        """
        Upvote the post by the user. If the user has already upvoted the post, update the vote type.
        :param user: User object
        :return: None
        """
        with transaction.atomic():
            post_vote, created = PostVote.objects.select_for_update().get_or_create(
                user=user, post=self, vote_type=PostVote.VoteType.UPVOTE
            )
            if not created and post_vote.vote_type != PostVote.VoteType.UPVOTE:
                post_vote.vote_type = PostVote.VoteType.UPVOTE
                post_vote.save()

    def downvote(self, user):
        """
        Downvote the post by the user. If the user has already downvoted the post, update the vote type.
        :param user: User object
        :return: None
        """
        with transaction.atomic():
            post_vote, created = PostVote.objects.select_for_update().get_or_create(
                user=user, post=self, vote_type=PostVote.VoteType.DOWNVOTE
            )
            if not created and post_vote.vote_type != PostVote.VoteType.DOWNVOTE:
                post_vote.vote_type = PostVote.VoteType.DOWNVOTE
                post_vote.save()

    def get_upvotes(self):
        """
        Get the number of upvotes for the post
        :return: int representing the number of upvotes
        """
        return PostVote.objects.filter(
            post=self, vote_type=PostVote.VoteType.UPVOTE
        ).count()

    def get_downvotes(self):
        """
        Get the number of downvotes for the post
        :return: int representing the number of downvotes
        """
        return PostVote.objects.filter(
            post=self, vote_type=PostVote.VoteType.DOWNVOTE
        ).count()


class Comment(models.Model):
    """
    Comment model representing a comment on a post.
    Fields:
    - comment_id: Primary key of the comment
    - post: Post the comment belongs to (foreign key to Post)
    - user: User who created the comment (foreign key to CustomUser)
    - text: Text of the comment
    - created_at: Date and time the comment was created
    - is_deleted: Boolean field indicating if the comment is deleted
    """
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        db_table = "comments"

    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    @property
    def votes(self):
        """
        Calculate the total votes of the comment
        :return: int representing the total votes
        """
        return self.get_upvotes() - self.get_downvotes()

    def clean(self):
        """
        Perform validation checks on the comment before saving
        :raises ValidationError: If the text field is empty or exceeds the maximum length
        :return: cleaned_data
        """
        cleaned_data = super().clean()
        if not self.text:
            raise ValidationError(_("Comment field is required."), code="invalid")
        if len(self.text) > 40000:
            raise ValidationError(
                _("Comment cannot exceed 40000 characters."), code="invalid"
            )
        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Save the comment and perform validation checks before saving
        """
        self.full_clean()
        super(Comment, self).save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        """
        Mark the comment as deleted and save it. The text is replaced with [deleted]
        :return: Comment object
        """
        self.text = "[deleted]"
        self.is_deleted = True
        self.save()
        return self

    def __str__(self):
        """
        String representation of the comment
        :return: First 50 characters of the comment text
        """
        return self.text[:50]

    def upvote(self, user):
        """
        Upvote the comment by the user. If the user has already upvoted the comment, update the vote type.
        :param user: User object
        :return: None
        """
        with transaction.atomic():
            (
                comment_vote,
                created,
            ) = CommentVote.objects.select_for_update().get_or_create(
                user=user, comment=self, vote_type=CommentVote.VoteType.UPVOTE
            )
            if not created and comment_vote.vote_type != CommentVote.VoteType.UPVOTE:
                comment_vote.vote_type = CommentVote.VoteType.UPVOTE
                comment_vote.save()

    def downvote(self, user):
        """
        Downvote the comment by the user. If the user has already downvoted the comment, update the vote type.
        :param user: User object
        :return: None
        """
        with transaction.atomic():
            (
                comment_vote,
                created,
            ) = CommentVote.objects.select_for_update().get_or_create(
                user=user, comment=self, vote_type=CommentVote.VoteType.DOWNVOTE
            )
            if not created and comment_vote.vote_type != CommentVote.VoteType.DOWNVOTE:
                comment_vote.vote_type = CommentVote.VoteType.DOWNVOTE
                comment_vote.save()

    def get_upvotes(self):
        """
        Get the number of upvotes for the comment
        :return: int representing the number of upvotes
        """
        return CommentVote.objects.filter(
            comment=self, vote_type=CommentVote.VoteType.UPVOTE
        ).count()

    def get_downvotes(self):
        """
        Get the number of downvotes for the comment
        :return: int representing the number of downvotes
        """
        return CommentVote.objects.filter(
            comment=self, vote_type=CommentVote.VoteType.DOWNVOTE
        ).count()


class Vote(models.Model):
    """
    Abstract model representing a vote.
    Fields:
    - user: User who voted (foreign key to CustomUser)
    - vote_type: Type of the vote (upvote or downvote)
    """
    class Meta:
        abstract = True

    class VoteType(models.TextChoices):
        """
        Enum representing the type of vote
        """
        UPVOTE = "up", _("Upvote")
        DOWNVOTE = "down", _("Downvote")

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, unique=False
    )  # One vote per user
    vote_type = models.CharField(
        max_length=4, choices=VoteType.choices, default=VoteType.UPVOTE
    )

    def __str__(self):
        """
        String representation of the vote
        :return: String indicating the user and the vote type
        """
        return f"{self.user} voted up" if self.vote_type else f"{self.user} voted down"

    def clean(self):
        """
        Perform validation checks on the vote before saving
        :raises ValidationError: If the user or vote_type fields are empty
        :return: cleaned_data
        """
        cleaned_data = super().clean()
        if not self.user_id:
            raise ValidationError(_("User field is required."), code="invalid")
        if not self.vote_type:
            raise ValidationError(_("Vote type field is required."), code="invalid")
        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Save the vote and perform validation checks before saving
        """
        self.full_clean()
        super(Vote, self).save(*args, **kwargs)


class PostVote(Vote):
    """
    PostVote model representing a vote on a post. Inherits from the Vote model.
    Fields:
    - post: Post the vote belongs to (foreign key to Post)
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # Compose primary key from user and post, one vote per user per post
    class Meta:
        unique_together = ["user", "post"]
        verbose_name = "Post Vote"
        verbose_name_plural = "Post Votes"
        db_table = "post_votes"

    def __str__(self):
        """
        String representation of the vote
        :return: String indicating the user and the vote type
        """
        return f"{self.user} voted up" if self.vote_type else f"{self.user} voted down"

    def clean(self):
        """
        Perform validation checks on the vote before saving
        :raises ValidationError: If the user or post fields are empty
        :raises ValidationError: If a vote with the same user and post already exists
        :return: cleaned_data
        """
        cleaned_data = super().clean()
        if not self.user_id:
            raise ValidationError(_("User field is required."), code="invalid")
        if not self.post_id:
            raise ValidationError(_("Post field is required."), code="invalid")
        if PostVote.objects.filter(user=self.user, post=self.post).exists() and not self.pk:
            raise ValidationError("Post Vote with this User already exists.")
        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Save the vote and perform validation checks before saving
        """
        self.full_clean()
        super(PostVote, self).save(*args, **kwargs)


class CommentVote(Vote):
    """
    CommentVote model representing a vote on a comment. Inherits from the Vote model.
    Fields:
    - comment: Comment the vote belongs to (foreign key to Comment)
    """
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    # Compose primary key from user and comment, one vote per user per comment
    class Meta:
        unique_together = ["user", "comment"]
        verbose_name = "Comment Vote"
        verbose_name_plural = "Comment Votes"
        db_table = "comment_votes"

    def __str__(self):
        """
        String representation of the vote
        :return: String indicating the user and the vote type
        """
        return f"{self.user} voted up" if self.vote_type else f"{self.user} voted down"

    def clean(self):
        """
        Perform validation checks on the vote before saving
        :raises ValidationError: If the user or comment fields are empty
        :return: cleaned_data
        """
        cleaned_data = super().clean()
        if not self.user_id:
            raise ValidationError(_("User field is required."), code="invalid")
        if not self.comment_id:
            raise ValidationError(_("Comment field is required."), code="invalid")
        if CommentVote.objects.filter(user=self.user, comment=self.comment).exists() and not self.pk:
            raise ValidationError("Comment Vote with this User already exists.")
        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Save the vote and perform validation checks before saving
        """
        self.full_clean()
        super(CommentVote, self).save(*args, **kwargs)
