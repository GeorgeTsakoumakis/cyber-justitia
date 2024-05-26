import unittest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import ProfessionalUser
from forum.models import Post, Comment
from chatbot.models import Session, Message
import json

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

    # Fails
    def test_update_details_with_valid_data(self):
        new_first_name = 'UpdatedFirstName'
        new_last_name = 'UpdatedLastName'
        new_email = 'updatedemail@example.com'

        response = self.client.post(reverse('dashboard'), {
            'first_name': new_first_name,
            'last_name': new_last_name,
            'email': new_email,
            'update_details': '1'
        })

        # Check that the user is redirected to the dashboard after a successful update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Fetch the updated user details from the database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_first_name)
        self.assertEqual(self.user.last_name, new_last_name)
        self.assertEqual(self.user.email, new_email)

    def test_update_first_name_with_blank_value(self):
        response = self.client.post(reverse('update_details'), {
            'first_name': '',
            'last_name': 'User',
            'email': 'testuser@example.com'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        form = response.context['update_details_form']
        self.assertTrue(form.errors)
        self.assertIn('first_name', form.errors)
        self.assertEqual(form.errors['first_name'], ['This field is required.'])

    def test_update_last_name_with_blank_value(self):
        response = self.client.post(reverse('update_details'), {
            'first_name': 'Test',
            'last_name': '',  # Attempting to update last name with a blank value
            'email': 'testuser@example.com'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        form = response.context['update_details_form']
        self.assertTrue(form.errors)
        self.assertIn('last_name', form.errors)
        self.assertEqual(form.errors['last_name'], ['This field is required.'])

    def test_update_password_with_valid_field(self):
        response = self.client.post(reverse('dashboard'), {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        })

        # Check that the password is updated successfully and the user is redirected
        self.assertEqual(response.status_code, 200)  # Redirect status code

        # Check that the new password works for login
        self.client.logout()
        login_response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'NewPassword123!'
        })
        self.assertEqual(login_response.status_code, 302)

    def test_change_password_mismatch(self):
        response = self.client.post(reverse('dashboard'), {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!',  # New passwords do not match
            'change_password': '1'  # Identify which form is being submitted
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        form = response.context['change_password_form']
        self.assertTrue(form.errors)
        self.assertIn('new_password2', form.errors)
        self.assertEqual(form.errors['new_password2'], ['The new passwords do not match.'])

    def test_change_password_with_blank_field(self):
        response = self.client.post(reverse('dashboard'), {
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
            'change_password': '1'
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.', 3)

    def test_deactivate_account_with_checkbox_checked(self):
        response = self.client.post(reverse('dashboard'), {
            'deactivate_profile': 'True',  # Checkbox checked
            'deactivate_account': '1'
        })

        # Check that the user is redirected to the index page after deactivation
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))

        # Fetch the updated user details from the database
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_deactivate_account_without_checkbox_checked(self):
        response = self.client.post(reverse('dashboard'), {
            'deactivate_account': '1'  # Add this to identify which form is being submitted
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

        # Fetch the updated user details from the database
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

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
    def test_update_flair_with_blank_value(self):
        response = self.client.post(reverse('update_flair'), {
            'flair': '',  # Attempting to update flair with a blank value
        })

        # Check that the form is re-rendered with errors
        self.assertEqual(response.status_code, 200)
        form = response.context['update_flair_form']
        self.assertTrue(form.errors)
        self.assertIn('flair', form.errors)
        self.assertEqual(form.errors['flair'], ['This field is required.'])


class ForumViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.staff_user = get_user_model().objects.create_user(
            username='staffuser',
            password='StaffPassword123!',
            email='staffuser@example.com',
            is_staff=True
        )
        self.post = Post.objects.create(
            title='Test Post',
            text='This is a test post.',
            user=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            text='This is a test comment.'
        )

    def test_access_forums_page(self):
        response = self.client.get(reverse('forums'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum.html')

    def test_view_post_detail(self):
        response = self.client.get(reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')

    def test_view_non_existent_post(self):
        response = self.client.get(reverse('post_detail', kwargs={'slug': 'non-existent-slug'}))
        self.assertEqual(response.status_code, 404)

    def test_create_post_with_valid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'title': 'New Post',
            'text': 'This is a new post.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_create_post_with_invalid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'title': '',
            'text': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'postcreation.html')
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('title', form.errors)
        self.assertIn('text', form.errors)

    def test_create_post_when_not_logged_in(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_create_comment_with_valid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.',
            'comment_form': '1'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='This is a new comment.').exists())

    # fails
    def test_create_comment_with_invalid_data(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forumpost.html')
        form = response.context['comment_form']
        self.assertTrue(form.errors)
        self.assertIn('comment', form.errors)
        self.assertContains(response, 'This field is required.')

    def test_create_comment_when_not_logged_in(self):
        response = self.client.post(reverse('create_comment', kwargs={'slug': self.post.slug}), {
            'comment': 'This is a new comment.'
        })
        self.assertRedirects(response, reverse('login'))

    def test_delete_post_as_post_owner(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_staff(self):
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertTrue(self.post.is_deleted)

    def test_delete_post_as_non_owner_non_staff(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='OtherPassword123!',
            email='otheruser@example.com'
        )
        self.client.login(username='otheruser', password='OtherPassword123!')
        response = self.client.post(reverse('delete_post', kwargs={'slug': self.post.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('forums'))
        self.post.refresh_from_db()
        self.assertFalse(self.post.is_deleted)

    def test_delete_comment_as_comment_owner(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_staff(self):
        self.client.login(username='staffuser', password='StaffPassword123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.is_deleted)

    def test_delete_comment_as_non_owner_non_staff(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='OtherPassword123!',
            email='otheruser@example.com'
        )
        self.client.login(username='otheruser', password='OtherPassword123!')
        response = self.client.post(reverse('delete_comment', kwargs={'slug': self.post.slug, 'comment_id': self.comment.comment_id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('post_detail', kwargs={'slug': self.post.slug}))
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_deleted)


class ChatbotViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com'
        )
        self.session = Session.objects.create(user=self.user)

    def test_access_chatbot_home(self):
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot_home.html')

    def test_access_chatbot_home_as_authenticated_user(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chatbot_session', kwargs={'session_id': self.session.session_id}))

    def test_access_chatbot_session(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': self.session.session_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chatbot_session.html')

    def test_access_non_existent_chatbot_session(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_access_another_users_chatbot_session(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='Password123!',
            email='otheruser@example.com'
        )
        other_session = Session.objects.create(user=other_user)
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('chatbot_session', kwargs={'session_id': other_session.session_id}))
        self.assertEqual(response.status_code, 404)

    def test_process_chat_message(self):
        self.client.login(username='testuser', password='Password123!')
        data = {
            'session_id': self.session.session_id,
            'message': 'Hello, chatbot!'
        }
        response = self.client.post(reverse('process_chat_message'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())

    def test_process_chat_message_when_not_authenticated(self):
        data = {
            'session_id': self.session.session_id,
            'message': 'Hello, chatbot!'
        }
        response = self.client.post(reverse('process_chat_message'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('response', response.json())

    def test_process_chat_message_with_invalid_method(self):
        response = self.client.get(reverse('process_chat_message'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('error'), 'Invalid request method')

    def test_create_new_session(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_session'))
        self.assertEqual(response.status_code, 302)
        new_session = Session.objects.latest('created_at')
        self.assertRedirects(response, reverse('chatbot_session', kwargs={'session_id': new_session.session_id}))


if __name__ == '__main__':
    unittest.main()
