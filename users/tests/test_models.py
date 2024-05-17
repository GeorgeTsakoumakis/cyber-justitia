import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

# Get the CustomUser model
CustomUser = get_user_model()


class CustomUserModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='password123'
        )

    def test_user_creation(self):
        # Check that the user is created correctly
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('password123'))

    def test_str_method(self):
        # Check the __str__ method
        self.assertEqual(str(self.user), 'testuser')

    def test_unique_email(self):
        # Check that emails are unique
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='anotheruser',
                first_name='Another',
                last_name='User',
                email='testuser@example.com',
                password='password123'
            )

    def test_email_format(self):
        # Check that invalid email format raises a ValidationError
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user8',
                first_name='Firstname',
                last_name='Lastname',
                email='invalid-email-format'
            )
            user.full_clean()

    def test_blank_names(self):
        # Check that first_name and last_name are not blank
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='user2',
                first_name='',
                last_name='Lastname',
                email='user2@example.com',
                password='password123'
            )

        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='user3',
                first_name='Firstname',
                last_name='',
                email='user3@example.com',
                password='password123'
            )

    def test_blank_username(self):
        # Check that username is not blank
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                first_name='Firstname',
                last_name='Lastname',
                email='user@example.com',
                password='password123'
            )


if __name__ == '__main__':
    unittest.main()
