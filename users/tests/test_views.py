import unittest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ProfessionalUser

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


class DashboardViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )
        self.client.force_login(self.user)

    def test_dashboard_page_access(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    # Will pass once dashboard implemented
    def test_update_details_with_valid_data(self):
        response = self.client.post(reverse('update_details'), {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updateduser@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(response, 'users/templates/dashboard.html')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'updateduser@example.com')

    # Will pass once dashboard implemented
    def test_update_first_name_with_invalid_data(self):
        response = self.client.post(reverse('dashboard'), {
            'first_name': '',
            'last_name': 'User',
            'email': 'updateduser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'First name field is required.')

    # Will pass once dashboard implemented
    def test_update_last_name_with_invalid_data(self):
        response = self.client.post(reverse('dashboard'), {
            'first_name': 'Test',
            'last_name': '',
            'email': 'updateduser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Last name field is required.')

    def test_change_password_with_valid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('dashboard'), {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_change_password_mismatch(self):
        response = self.client.post(reverse('dashboard'), {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'The new passwords do not match.')

    def test_deactivate_account_with_checkbox_checked(self):
        self.client.force_login(self.user)  # Ensure the user is logged in
        response = self.client.post(reverse('dashboard'), {
            'deactivate_profile': True
        })
        self.assertRedirects(response, reverse('index'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    # Will pass once dashboard implemented
    def test_deactivate_account_without_checkbox_checked(self):
        self.client.force_login(self.user)  # Ensure the user is logged in
        response = self.client.post(reverse('dashboard'), {
            'deactivate_profile': False
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Checkbox is required.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)  # Ensure the account is still active

    def test_update_description_with_valid_data(self):
        response = self.client.post(reverse('update_description'), {
            'description': 'Updated description'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.description, 'Updated description')

    def test_update_flair_with_valid_data(self):
        response = self.client.post(reverse('update_flair'), {
            'flair': 'Updated flair'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.user.professionaluser.refresh_from_db()
        self.assertEqual(self.user.professionaluser.flair, 'Updated flair')

    # Will pass once dashboard implemented
    def test_update_flair_blank(self):
        response = self.client.post(reverse('dashboard'), {
            'flair': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Flair field is required.')


if __name__ == '__main__':
    unittest.main()
