import unittest

from django.contrib.auth.password_validation import validate_password
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from users.models import ProfessionalUser, Education, Employments
import datetime

# Get the CustomUser model
CustomUser = get_user_model()


class CustomUserModelTest(TestCase):
    """
    Test case for the CustomUser model.
    """

    def setUp(self):
        """
        TUM1: Set up a test user for use in the tests.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_user_creation(self):
        """
        TUM2: Test that the user is created correctly with the provided attributes.
        """
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('Password123!'))

    def test_str_method(self):
        """
        TUM3: Test the __str__ method of the user model.
        """
        self.assertEqual(str(self.user), 'testuser')

    def test_unique_email(self):
        """
        TUM4: Test that the email field enforces uniqueness.
        """
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='anotheruser',
                first_name='Another',
                last_name='User',
                email='testuser@example.com',
                password='Password123!'
            )

    def test_email_format(self):
        """
        TUM5: Test that an invalid email format raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='user8',
                first_name='Firstname',
                last_name='Lastname',
                email='invalid-email-format'
            )
            user.full_clean()

    def test_blank_names(self):
        """
        TUM6: Test that first_name and last_name fields cannot be blank.
        """
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
        """
        TUM7: Test that the username field cannot be blank.
        """
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username='',
                first_name='Firstname',
                last_name='Lastname',
                email='user@example.com',
                password='Password123!'
            )

    def test_duplicate_username(self):
        """
        TUM8: Test that the username field enforces uniqueness.
        """
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='testuser',
                first_name='Another',
                last_name='User',
                email='anotheruser@example.com',
                password='Password123!'
            )

    def test_default_is_banned(self):
        """
        TUM9: Test that the is_banned field defaults to False.
        """
        self.assertFalse(self.user.is_banned)

    def test_max_length_constraints(self):
        """
        TUM10: Test that the max length constraints are enforced for various fields.
        """
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
        """
        TUM11: Test that a username with special characters raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            user = CustomUser(
                username='!@#%$%',
                first_name='Firstname',
                last_name='Lastname',
                email='user11@example.com',
                password='Password123!'
            )
            user.full_clean()

    def test_whitespace_username(self):
        """
        TUM12: Test that a username with only whitespace raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            user = CustomUser(username='   ')
            user.full_clean()

    def test_whitespace_names(self):
        """
        TUM13: Test that first_name and last_name fields with only whitespace raise a ValidationError.
        """
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
        """
        TUM14: Test that an email with leading or trailing whitespace raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            user = CustomUser(username='user8', email='   valid@example.com   ')
            user.full_clean()

    def test_invalid_password(self):
        """
        TUM15: Test that an invalid password raises a ValidationError.
        """
        invalid_password = 'cringe'

        with self.assertRaises(ValidationError):
            validate_password(invalid_password, user=self.user)


class ProfessionalUserModelTest(TestCase):
    """
    Test case for the ProfessionalUser model.
    """

    def setUp(self):
        """
        TUM16: Set up a test user for use in the tests.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com',
            password='Password123!'
        )

    def test_create_professional_user(self):
        """
        TUM17: Test creating a professional user with a flair.
        """
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        self.assertIsInstance(professional_user, ProfessionalUser)
        self.assertEqual(professional_user.flair, "Experienced Attorney")

    def test_blank_flair(self):
        """
        TUM18: Test that a blank flair raises a ValidationError.
        """
        professional_user = ProfessionalUser(user=self.user, flair="")
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_max_flair_length(self):
        """
        TUM19: Test that the flair field allows a maximum length of 100 characters.
        """
        flair = 'a' * 100
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair=flair
        )
        self.assertEqual(professional_user.flair, flair)

    def test_long_flair(self):
        """
        TUM20: Test that a flair longer than 100 characters raises a ValidationError.
        """
        flair = 'a' * 101
        professional_user = ProfessionalUser(user=self.user, flair=flair)
        with self.assertRaises(ValidationError):
            professional_user.full_clean()

    def test_update_flair(self):
        """
        TUM21: Test updating the flair of a professional user.
        """
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney"
        )
        professional_user.flair = "Expert Legal Advisor"
        professional_user.save()
        professional_user.refresh_from_db()
        self.assertEqual(professional_user.flair, "Expert Legal Advisor")

    def test_valid_reason_banned(self):
        """
        TUM22: Test creating a professional user with a valid reason_banned.
        """
        user = CustomUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned="Violation of terms"
        )
        self.assertIsInstance(user, CustomUser)
        self.assertEqual(user.reason_banned, "Violation of terms")

    def test_blank_reason_banned(self):
        """
        TUM23: Test that a blank reason_banned is allowed.
        """
        professional_user = ProfessionalUser.objects.create(
            user=self.user,
            flair="Experienced Attorney",
            reason_banned=""
        )
        self.assertEqual(professional_user.reason_banned, "")


class EducationModelTest(TestCase):
    """
    Test case for the Education model.
    """

    def setUp(self):
        """
        TUM24: Set up a test user and professional user for use in the tests.
        """
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
        """
        TUM25: Test creating a valid education record.
        """
        education = Education(
            prof_id=self.professional_user,
            school_name='Test University',
            degree='Bachelor of Science',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        education.full_clean()  # Should not raise any errors

    def test_school_name_cannot_be_blank(self):
        """
        TUM26: Test that school_name field cannot be blank.
        """
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
        """
        TUM27: Test that degree field cannot be blank.
        """
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
        """
        TUM28: Test that start_date field cannot be blank.
        """
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
        """
        TUM29: Test that school_name field cannot exceed max length of 100 characters.
        """
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
        """
        TUM30: Test that degree field cannot exceed max length of 100 characters.
        """
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
        """
        TUM31: Test that start_date cannot be in the future.
        """
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
        """
        TUM32: Test that end_date field can be blank.
        """
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


class EmploymentModelTest(TestCase):
    """
    Test case for the Employment model.
    """

    def setUp(self):
        """
        TUM33: Set up a test user and professional user for use in the tests.
        """
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

    def test_valid_employment_creation(self):
        """
        TUM34: Test creating a valid employment record.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='Software Engineer',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        employment.full_clean()  # Should not raise any errors

    def test_company_cannot_be_blank(self):
        """
        TUM35: Test that company field cannot be blank.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='',
            position='Software Engineer',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('company', context.exception.message_dict)

    def test_position_cannot_be_blank(self):
        """
        TUM36: Test that position field cannot be blank.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('position', context.exception.message_dict)

    def test_start_date_cannot_be_blank(self):
        """
        TUM37: Test that start_date field cannot be blank.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='Software Engineer',
            start_date=None,
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('start_date', context.exception.message_dict)

    def test_company_cannot_exceed_max_length(self):
        """
        TUM38: Test that company field cannot exceed max length of 100 characters.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='A' * 101,
            position='Software Engineer',
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('company', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['company'], ['Ensure this value has at most 100 characters (it has 101).'])

    def test_position_cannot_exceed_max_length(self):
        """
        TUM39: Test that position field cannot exceed max length of 100 characters.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='A' * 101,
            start_date=datetime.date(2015, 9, 1),
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('position', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['position'], ['Ensure this value has at most 100 characters (it has 101).'])

    def test_start_date_cannot_be_in_future(self):
        """
        TUM40: Test that start_date cannot be in the future.
        """
        future_date = datetime.date.today() + datetime.timedelta(days=100)
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='Software Engineer',
            start_date=future_date,
            end_date=datetime.date(2019, 6, 30)
        )
        with self.assertRaises(ValidationError) as context:
            employment.full_clean()
        self.assertIn('start_date', context.exception.message_dict)
        self.assertEqual(context.exception.message_dict['start_date'], ['Start date cannot be in the future.'])

    def test_end_date_can_be_blank(self):
        """
        TUM41: Test that end_date field can be blank.
        """
        employment = Employments(
            prof_id=self.professional_user,
            company='Test Company',
            position='Software Engineer',
            start_date=datetime.date(2015, 9, 1),
            end_date=None
        )
        try:
            employment.full_clean()  # Should not raise any errors
        except ValidationError:
            self.fail('This should not happen.')


if __name__ == '__main__':
    unittest.main()