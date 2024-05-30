from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model
from forum.models import Post, Comment


class UserProfilePageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword123!',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.post = Post.objects.create(
            title='Test Post',
            text='This is a test post.',
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

        # Verify URL starts with the expected base path
        current_url = page.url
        expected_base_url = self.live_server_url + "/chatbot/"
        assert current_url.startswith(expected_base_url), f"Unexpected URL: {current_url}"

    def test_user_profile_page(self):
        """
        TFE3: Test profile page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            self.login(page, 'adminuser', 'AdminPassword123!')

            # Navigate to the user profile page
            profile_url = self.live_server_url + reverse('profile', args=[self.user.username])
            page.goto(profile_url)

            # Verify user profile details
            assert page.is_visible(f"text={self.user.first_name} {self.user.last_name}")
            assert page.is_visible(f"text={self.user.email}")

            # Verify recent posts
            assert page.is_visible("text=Recent posts")
            assert page.is_visible(f"text={self.post.title}")
            assert page.is_visible(f"text={self.post.text}")

            # Verify recent comments
            assert page.is_visible("text=Recent comments")
            assert page.is_visible(f"text={self.comment.post.title}")
            assert page.is_visible(f"text={self.comment.text}")

            page.close()
            browser.close()
