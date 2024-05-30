from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import sync_playwright
from django.contrib.auth import get_user_model

class DashboardPageTest(StaticLiveServerTestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )

    def login(self, page):
        page.goto(self.live_server_url + reverse('login'))
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="password"]', 'Password123!')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        print("Current URL after login:", page.url)
        current_url = page.url
        expected_base_url = self.live_server_url + "/chatbot/"
        assert current_url.startswith(expected_base_url), f"Unexpected URL: {current_url}"

    def test_dashboard_page(self):
        """
        TFE4: Test dashboard page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            self.login(page)

            # Navigate to the dashboard page
            page.goto(self.live_server_url + reverse('dashboard'))

            # Test 1: Update user details
            page.fill('input[name="first_name"]', "UpdatedTest")
            page.fill('input[name="last_name"]', "UpdatedUser")
            page.fill('input[name="email"]', "updateduser@example.com")
            page.click('button[name="update_details"]')

            # Check for successful update message
            page.wait_for_selector('text=Details updated successfully')
            self.assertTrue(page.is_visible("text=Details updated successfully"))

            # Test 2: Change password
            page.fill('input[name="old_password"]', 'Password123!')
            page.fill('input[name="new_password1"]', 'NewPassword123!')
            page.fill('input[name="new_password2"]', 'NewPassword123!')
            page.click('button[name="change_password"]')

            # Check for successful password update message
            page.wait_for_selector('text=Password updated successfully')
            self.assertTrue(page.is_visible("text=Password updated successfully"))

            # Test 3: Update description
            page.fill('textarea[name="description"]', 'This is an updated description.')
            page.click('button[name="update_description"]')

            # Check for successful description update message
            page.wait_for_selector('text=Description updated successfully')
            self.assertTrue(page.is_visible("text=Description updated successfully"))

            # Test 4: Deactivate account
            page.check('input[name="deactivate_profile"]')
            page.click('button[name="deactivate_account"]')

            # Check for successful account deactivation message
            page.wait_for_selector('text=Account deactivated successfully')
            self.assertTrue(page.is_visible("text=Account deactivated successfully"))

            page.close()
            browser.close()
