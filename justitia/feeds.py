from django.contrib.syndication.views import Feed
from forum.models import Post


class LatestPostsFeed(Feed):
    """
    RSS Feed for the latest posts on Justitia.
    Install Feedly or another RSS reader extension to view and subscribe to this feed.
    """
    title = "Justitia - Latest Posts"
    link = "/forum/"
    description = "The latest posts on Justitia."

    def items(self):
        return Post.objects.filter(is_deleted=False).order_by("-created_at")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text

    def item_link(self, item):
        return item.get_url()

    def item_pubdate(self, item):
        return item.created_at
