import unittest

from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import auth
from ..models import ProfessionalUser
from chatbot.models import Session

CustomUser = get_user_model()

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_render_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_unauthenticated_user_accesses_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_authenticated_user_accesses_register_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, '/chatbot/', target_status_code=302)

    def test_register_new_standard_user_with_valid_data(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'Password123!',
            'password2': 'Password123!',
            'user_type': 'standard'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(CustomUser.objects.filter(username='johndoe').exists())

    def test_register_new_professional_user_with_valid_data(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': 'janedoe',
            'email': 'janedoe@example.com',
            'password': 'Password123!',
            'password2': 'Password123!',
            'user_type': 'professional',
            'flair': 'Experienced Attorney'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(CustomUser.objects.filter(username='janedoe').exists())
        self.assertTrue(ProfessionalUser.objects.filter(user__username='janedoe').exists())

    def test_register_user_with_weak_password(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'weak',
            'password2': 'weak',
            'user_type': 'standard'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password not strong enough')

    def test_register_user_with_non_matching_passwords(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'johndoe@example.com',
            'password': 'Strongpassword123!',
            'password2': 'differentpassword',
            'user_type': 'standard'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password not matching')

    def test_register_user_with_existing_username(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'testuser',  # existing username
            'email': 'johndoe@example.com',
            'password': 'Password123!',
            'password2': 'Password123!',
            'user_type': 'standard'
        }, follow=True)
        self.assertRedirects(response, reverse('register'))
        self.assertContains(response, 'Username already exists')

    def test_register_user_with_existing_email(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'testuser@example.com',  # existing email
            'password': 'Password123!',
            'password2': 'Password123!',
            'user_type': 'standard'
        }, follow=True)
        self.assertRedirects(response, reverse('register'))
        self.assertContains(response, 'Email already exists')

    def test_unauthenticated_user_accesses_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_authenticated_user_accesses_login_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, '/chatbot/', target_status_code=302)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'Password123!'
        })
        self.assertRedirects(response, '/chatbot/', target_status_code=302)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, 'Invalid credentials')

    def test_authenticated_user_logs_out(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_authenticated_user_accesses_profile_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'templates/user_profile.html')
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)


if __name__ == '__main__':
    unittest.main()
