from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from forum.models import Post

class ForumPageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='Password123!',
            email='testuser2@example.com',
            first_name='Test2',
            last_name='User2'
        )
        self.post = Post.objects.create(
            title='Initial Post',
            text='This is the initial post.',
            user=self.user
        )

    def login(self, page, username, password):
        page.goto(self.live_server_url + reverse('login'))
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

    def test_forum_page(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            self.login(page, 'testuser', 'Password123!')

            # Navigate to the forum page
            forum_url = self.live_server_url + reverse('forums')
            page.goto(forum_url)

            # Verify initial post is present
            assert page.is_visible(f"text={self.post.title}")
            assert page.is_visible(f"text={self.post.text}")

            # Create a new post
            page.click('a[href*="create_post"]')
            page.fill('input[name="title"]', 'New Post')
            page.fill('textarea[name="text"]', 'This is a new post.')
            page.click('button[type="submit"]')

            # Verify the new post appears
            page.goto(forum_url)
            assert page.is_visible(f"text=New Post")
            assert page.is_visible(f"text=This is a new post.")

            # Vote on a post
            initial_vote_count = int(page.inner_text(f'#upvote-count-{self.post.post_id}'))
            page.click(f'div[data-id="{self.post.post_id}"] .button_upvote')
            page.wait_for_selector(f'#upvote-count-{self.post.post_id}')
            new_vote_count = int(page.inner_text(f'#upvote-count-{self.post.post_id}'))
            assert new_vote_count == initial_vote_count + 1

            page.close()
            browser.close()
