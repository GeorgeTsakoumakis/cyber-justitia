from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model

class LoginPageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )

    def test_login_page(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the login page
            page.goto(self.live_server_url + reverse('login'))

            # Test 1: Successful login
            page.fill('input[name="username"]', 'testuser')
            page.fill('input[name="password"]', 'Password123!')
            page.click('button[type="submit"]')

            # Verify successful login by checking the URL or a specific element on the landing page
            page.wait_for_load_state('networkidle')
            current_url = page.url
            expected_base_url = self.live_server_url + "/chatbot/"
            assert current_url.startswith(expected_base_url), f"Unexpected URL: {current_url}"

            # Logout
            page.goto(self.live_server_url + reverse('logout'))

            # Test 2: Unsuccessful login (incorrect password)
            page.goto(self.live_server_url + reverse('login'))
            page.fill('input[name="username"]', 'testuser')
            page.fill('input[name="password"]', 'WrongPassword!')
            page.click('button[type="submit"]')

            # Verify error message
            page.wait_for_selector('text=Invalid credentials')
            assert page.is_visible("text=Invalid credentials")

            # Test 3: Unsuccessful login (nonexistent user)
            page.goto(self.live_server_url + reverse('login'))
            page.fill('input[name="username"]', 'nonexistentuser')
            page.fill('input[name="password"]', 'Password123!')
            page.click('button[type="submit"]')

            # Verify error message
            page.wait_for_selector('text=Invalid credentials')
            assert page.is_visible("text=Invalid credentials")

            page.close()
            browser.close()
