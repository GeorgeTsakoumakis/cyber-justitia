from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from django.urls import reverse


class RegisterPageTest(StaticLiveServerTestCase):

    def test_register_page(self):
        """
        TFE2: Test registration page.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.live_server_url + reverse('register'))

            # Test 1: Successful Registration
            page.fill('input[name="first_name"]', "Test")
            page.fill('input[name="last_name"]', "User")
            page.fill('input[name="email"]', "testuser@example.com")
            page.fill('input[name="username"]', "testuser")
            page.fill('input[name="password"]', "Password123!")
            page.fill('input[name="password2"]', "Password123!")
            page.check('input#flexRadioDefault1')  # Standard user
            page.click('button[type="submit"]')

            # Check for successful redirection to login page
            page.wait_for_load_state('networkidle')
            self.assertEqual(page.url, self.live_server_url + reverse('login'))

            # Test 2: Password Mismatch
            page.goto(self.live_server_url + reverse('register'))
            page.fill('input[name="first_name"]', "Test")
            page.fill('input[name="last_name"]', "User")
            page.fill('input[name="email"]', "testuser2@example.com")
            page.fill('input[name="username"]', "testuser2")
            page.fill('input[name="password"]', "Password123!")
            page.fill('input[name="password2"]', "DifferentPassword123!")
            page.check('input#flexRadioDefault1')
            page.click('button[type="submit"]')

            # Check for password mismatch error message
            page.wait_for_selector('text=Password not matching')
            self.assertTrue(page.is_visible("text=Password not matching"))

            # Test 3: Username already exists
            page.goto(self.live_server_url + reverse('register'))
            page.fill('input[name="first_name"]', "Test")
            page.fill('input[name="last_name"]', "User")
            page.fill('input[name="email"]', "testuser2@example.com")
            page.fill('input[name="username"]', "testuser")  # Already exists
            page.fill('input[name="password"]', "Password123!")
            page.fill('input[name="password2"]', "Password123!")
            page.check('input#flexRadioDefault1')
            page.click('button[type="submit"]')

            # Check for username exists error message
            page.wait_for_selector('text=Username already exists')
            self.assertTrue(page.is_visible("text=Username already exists"))

            # Test 4: Email already exists
            page.goto(self.live_server_url + reverse('register'))
            page.fill('input[name="first_name"]', "Test")
            page.fill('input[name="last_name"]', "User")
            page.fill('input[name="email"]', "testuser@example.com")  # Already exists
            page.fill('input[name="username"]', "testuser3")
            page.fill('input[name="password"]', "Password123!")
            page.fill('input[name="password2"]', "Password123!")
            page.check('input#flexRadioDefault1')
            page.click('button[type="submit"]')

            # Check for email exists error message
            page.wait_for_selector('text=Email already exists')
            self.assertTrue(page.is_visible("text=Email already exists"))

            page.close()
            browser.close()
