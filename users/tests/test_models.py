import unittest

from django.contrib.auth.password_validation import validate_password
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from ..models import ProfessionalUser

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
            password='Password123!'
        )

    def test_user_creation(self):
        # Check that the user is created correctly
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('Password123!'))

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
                password='Password123!'
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
        user = CustomUser(
            username='user2',
            first_name='',
            last_name='Lastname',
            email='user2@example.com',
            password='Password123!'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

        user = CustomUser(
            username='user3',
            first_name='Firstname',
            last_name='',
            email='user3@example.com',
            password='Password123!'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_blank_username(self):
        # Check that username is not blank
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                first_name='Firstname',
                last_name='Lastname',
                email='user@example.com',
                password='Password123!'
            )

    def test_duplicate_username(self):
        # Check that usernames are unique
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='testuser',
                first_name='Another',
                last_name='User',
                email='anotheruser@example.com',
                password='Password123!'
            )

    def test_default_is_banned(self):
        # Check that is_banned defaults to False
        self.assertFalse(self.user.is_banned)

    def test_max_length_constraints(self):
        # Check max length constraints
        long_username = 'a' * 151  # lots of a's
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username=long_username,
                first_name='Firstname',
                last_name='Lastname',
                email='user4@example.com'
            )
            user.full_clean()

        long_first_name = 'a' * 151
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user5',
                first_name=long_first_name,
                last_name='Lastname',
                email='user5@example.com'
            )
            user.full_clean()

        long_last_name = 'a' * 151
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user6',
                first_name='Firstname',
                last_name=long_last_name,
                email='user6@example.com'
            )
            user.full_clean()

        long_email = 'a' * 321 + '@example.com'
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user7',
                first_name='Firstname',
                last_name='Lastname',
                email=long_email
            )
            user.full_clean()

        long_description = 'a' * 257
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user8',
                first_name='Firstname',
                last_name='Lastname',
                email='user8@example.com',
                description=long_description
            )
            user.full_clean()

    def test_username_with_special_characters(self):
        with (self.assertRaises(ValidationError)):
            user = CustomUser(
                username='!@#%$%',
                first_name='Firstname',
                last_name='Lastname',
                email='user11@example.com',
                password='Password123!'
            )
            user.full_clean()

    def test_whitespace_username(self):
        with self.assertRaises(ValidationError):
            user = CustomUser(username='   ')
            user.full_clean()

    def test_whitespace_names(self):
        # Check that first_name and last_name are not blank
        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create_user(
                username='user2',
                first_name='     ',
                last_name='Lastname',
                email='user2@example.com',
                password='Password123!'
            )
            user.full_clean()

        with self.assertRaises(ValidationError):
            user = CustomUser.objects.create_user(
                username='user3',
                first_name='Firstname',
                last_name='     ',
                email='user3@example.com',
                password='Password123!'
            )
            user.full_clean()

    def test_whitespace_email(self):
        with self.assertRaises(ValidationError):
            user = CustomUser(username='user8', email='   valid@example.com   ')
            user.full_clean()

    def test_invalid_password(self):
        # Check that an invalid password raises a ValidationError
        invalid_password = 'cringe'

        with self.assertRaises(ValidationError):
            validate_password(invalid_password, user=self.user)


class ProfessionalUserModelTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_create_professional_user(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        self.assertIsInstance(professional_user, ProfessionalUser)
        self.assertEqual(professional_user.flair, "Experienced Attorney")

    def test_blank_flair(self):
        professional_user = ProfessionalUser(user=self.user, flair="")
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_max_flair_length(self):
        flair = 'a' * 100
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair=flair
        )
        self.assertEqual(professional_user.flair, flair)

    def test_long_flair(self):
        flair = 'a' * 101
        professional_user = ProfessionalUser(user=self.user, flair=flair)
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_update_flair(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        professional_user.flair = "Expert Legal Advisor"
        professional_user.save()
        professional_user.refresh_from_db()
        self.assertEqual(professional_user.flair, "Expert Legal Advisor")


if __name__ == '__main__':
    unittest.main()
