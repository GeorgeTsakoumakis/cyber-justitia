from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from forum.models import Post, Comment


class PostDetailPageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.post = Post.objects.create(
            title='Initial Post',
            text='This is the initial post.',
            user=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            text='This is a test comment.',
            user=self.user
        )

    def login(self, page, username, password):
        page.goto(self.live_server_url + reverse('login'))
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

    def test_post_detail_page(self):
        """
        TFE7: Test forum post page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            self.login(page, 'testuser', 'Password123!')

            # Navigate to the post detail page
            post_detail_url = self.live_server_url + reverse('post_detail', args=[self.post.slug])
            page.goto(post_detail_url)

            # Verify  post and comment are present
            assert page.is_visible(f"text={self.post.title}")
            assert page.is_visible(f"text={self.post.text}")
            assert page.is_visible(f"text={self.comment.text}")

            page.close()
            browser.close()
