from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, PostVote, CommentVote


class CreatePostForm(forms.ModelForm):
    """
    Form for creating a new post. It includes fields for the title and text of the post.
    """

    class Meta:
        model = Post
        fields = ["title", "text"]

    title = forms.CharField(
        label=_("Title"),
        max_length=256,
        error_messages={
            "required": _("Title field is required."),
            "max_length": _("Title cannot exceed 256 characters."),
        },
    )

    text = forms.CharField(
        label=_("Text"),
        max_length=40000,
        widget=forms.Textarea(attrs={"rows": 10, "cols": 40}),
        error_messages={
            "required": _("Text field is required."),
            "max_length": _("Text cannot exceed 40000 characters."),
        },
    )

    def clean_title(self):
        """
        Check if the title is empty or exceeds allowed character limit.
        """
        title = self.cleaned_data["title"]
        if not title:
            raise forms.ValidationError(_("Title field is required."), code="invalid")
        if len(title) > 256:
            raise forms.ValidationError(
                _("Title cannot exceed 256 characters."), code="invalid"
            )
        return title

    def clean_text(self):
        """
        Check if the text is empty or exceeds allowed character limit.
        """
        text = self.cleaned_data["text"]
        if not text:
            raise forms.ValidationError(_("Text field is required."), code="invalid")
        if len(text) > 40000:
            raise forms.ValidationError(
                _("Text cannot exceed 40000 characters."), code="invalid"
            )
        return text


class CreateCommentForm(forms.Form):
    """
    Form for creating a new comment. It includes a field for the comment text.
    """

    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        error_messages={
            "required": _("Comment field is required."),
            "max_length": _("Comment cannot exceed 40000 characters."),
        },
    )

    def clean_comment(self):
        """
        Check if the comment is empty or exceeds allowed character limit.
        """
        comment = self.cleaned_data["comment"]
        if not comment:
            raise forms.ValidationError(_("Comment field is required."), code="invalid")
        if len(comment) > 40000:
            raise forms.ValidationError(
                _("Comment cannot exceed 40000 characters."), code="invalid"
            )
        return comment


class VoteForm(forms.Form):
    """
    Form for voting on a post or comment. It includes a field for the vote type.
    """

    VOTE_CHOICES = [("up", "Upvote"), ("down", "Downvote")]

    vote_type = forms.ChoiceField(
        label=_("Vote"),
        choices=VOTE_CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            "invalid": _("Invalid vote type."),
        },
    )

    class Meta:
        abstract = True
        fields = ["vote_type"]

    def clean_vote_type(self):
        """
        Check if the vote type is valid.
        """
        vote_type = self.cleaned_data["vote_type"]
        # if vote_type is not one of the first elements in every tuple in VOTE_CHOICES
        if vote_type not in [choice[0] for choice in self.VOTE_CHOICES]:
            raise forms.ValidationError(_("Invalid vote type."), code="invalid")
        return vote_type


class PostVoteForm(VoteForm):
    """
    Form for voting on a post. It includes a field for the vote type.
    """

    class Meta:
        model = PostVote
        fields = ["vote_type"]


class CommentVoteForm(VoteForm):
    """
    Form for voting on a comment. It includes a field for the vote type.
    """

    class Meta:
        model = CommentVote
        fields = ["vote_type"]
