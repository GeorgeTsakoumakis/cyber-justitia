"""
Registering the models in the admin panel.

Author: Georgios Tsakoumakis
"""

from django.contrib import admin
from .models import Post, Comment, PostVote, CommentVote

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostVote)
admin.site.register(CommentVote)
