from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model


class BanUserPageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username='adminuser',
            password='AdminPassword123!',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.user_to_ban = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )

    def login_as_superuser(self, page):
        page.goto(self.live_server_url + reverse('login'))
        page.fill('input[name="username"]', 'adminuser')
        page.fill('input[name="password"]', 'AdminPassword123!')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        # Verify URL starts with the expected base path
        current_url = page.url
        expected_base_url = self.live_server_url + "/chatbot/"
        assert current_url.startswith(expected_base_url), f"Unexpected URL: {current_url}"

    def test_ban_user_page(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            self.login_as_superuser(page)

            # Navigate to the ban user page
            ban_url = self.live_server_url + reverse('ban_user', args=[self.user_to_ban.username])
            page.goto(ban_url)

            # Fill out the ban form
            page.fill('textarea[name="reason_banned"]', "Violation of community guidelines.")
            page.check('input[name="confirm_ban"]')
            page.click('button[type="submit"]')

            # Check for successful ban message
            page.wait_for_selector('text=User testuser has been banned')
            self.assertTrue(page.is_visible("text=User testuser has been banned"))

            page.close()
            browser.close()
