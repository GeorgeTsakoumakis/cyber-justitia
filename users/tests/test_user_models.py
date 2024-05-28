import unittest

from django.contrib.auth.password_validation import validate_password
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from users.models import ProfessionalUser, Education
import datetime

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

    def test_valid_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned="Violation of terms"
        )
        self.assertIsInstance(professional_user, ProfessionalUser)
        self.assertEqual(professional_user.reason_banned, "Violation of terms")

    def test_blank_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=""
        )
        self.assertEqual(professional_user.reason_banned, "")

    def test_null_reason_banned(self):
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=None
        )
        self.assertIsNone(professional_user.reason_banned)

    def test_max_reason_banned_length(self):
        reason_banned = 'a' * 150
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=reason_banned
        )
        self.assertEqual(professional_user.reason_banned, reason_banned)

    def test_long_reason_banned(self):
        reason_banned = 'a' * 151
        professional_user = ProfessionalUser(user=self.user, flair="Experienced Attorney", reason_banned=reason_banned)
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_create_professional_without_user(self):
        professional_user = ProfessionalUser(user=None, flair="Experienced Attorney")
        with self.assertRaises(IntegrityError):
            professional_user.save()

    def test_delete_associated_user(self):
        # Checks if ProfessionalUser deletes itself when the associated User is deleted
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        self.user.delete()
        with self.assertRaises(ProfessionalUser.DoesNotExist):
            ProfessionalUser.objects.get(pk=professional_user.prof_id)


class EducationModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair='Initial Flair'
        )

    def test_valid_education_creation(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='Bachelor of Science',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        education.full_clean()  # Should not raise any errors

    def test_school_name_cannot_be_blank(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='',
            degree='Bachelor of Science',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('school_name', context.exception.message_dict)

    def test_degree_cannot_be_blank(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('degree', context.exception.message_dict)

    def test_start_date_cannot_be_blank(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='Bachelor of Science',
            start_date=None,
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('start_date', context.exception.message_dict)

    def test_school_name_cannot_exceed_max_length(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='A' * 101,
            degree='Bachelor of Science',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('school_name', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['school_name'], ['Ensure this value has at most 100 characters (it has 101).'])

    def test_degree_cannot_exceed_max_length(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='A' * 101,
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('degree', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['degree'], ['Ensure this value has at most 100 characters (it has 101).'])

    def test_start_date_cannot_be_in_future(self):
        future_date = datetime.date.today() + datetime.timedelta(days=100)
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='Bachelor of Science',
            start_date=future_date,
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            education.full_clean()
        self.assertIn('start_date', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['start_date'], ['Start date cannot be in the future.'])

    def test_end_date_can_be_blank(self):
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='Bachelor of Science',
            start_date=datetime.date(2015, 9, 1),
            end_date=None
        )
        try:
            education.full_clean()  # Should not raise any errors
        except ValidationError:
            self.fail('This should not happen.')



if __name__ == '__main__':
    unittest.main()