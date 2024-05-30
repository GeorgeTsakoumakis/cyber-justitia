"""
Test cases for user-related forms.

Author: Ionut-Valeriu Facaeru, Georgios Tsakoumakis
"""

import unittest
from django.test import TestCase
from users.forms import (UpdateDetailsForm, UpdatePasswordForm, UpdateDescriptionForm, DeactivateAccountForm,
                         UpdateFlairForm, UpdateEmploymentsForm, UpdateEducationForm, BanForm)
from users.models import CustomUser, ProfessionalUser, Employments, Education
from datetime import date, timedelta


class UserFormTests(TestCase):
    """
    Test case for user-related forms.
    """

    def setUp(self):
        """
        TUF1: Set up a test user and professional user for use in the tests.
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

    def test_valid_user_details_update(self):
        """
        TUF2: Test updating user details with valid data.
        """
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_user_details_update_with_empty_first_name(self):
        """
        TUF3: Test updating user details with an empty first name.
        """
        form_data = {
            'first_name': '',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_user_details_update_with_empty_last_name(self):
        """
        TUF4: Test updating user details with an empty last name.
        """
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': '',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_user_details_update_with_empty_email(self):
        """
        TUF5: Test updating user details with an empty email.
        """
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': ''
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_details_update_with_first_name_exceeding_max_length(self):
        """
        TUF6: Test updating user details with a first name exceeding max length.
        """
        form_data = {
            'first_name': 'a' * 151,
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_user_details_update_with_last_name_exceeding_max_length(self):
        """
        TUF7: Test updating user details with a last name exceeding max length.
        """
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'a' * 151,
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_user_details_update_with_duplicate_email(self):
        """
        TUF8: Test updating user details with a duplicate email.
        """
        CustomUser.objects.create_user(
            username='otheruser',
            password='Password123!',
            email='duplicate@example.com'
        )
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'duplicate@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['This email is already in use.'])

    def test_valid_password_update(self):
        """
        TUF9: Test updating the password with valid data.
        """
        form_data = {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        form = UpdatePasswordForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_password_update_with_incorrect_old_password(self):
        """
        TUF10: Test updating the password with an incorrect old password.
        """
        form_data = {
            'old_password': 'WrongPassword123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        form = UpdatePasswordForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('old_password', form.errors)
        self.assertEqual(form.errors['old_password'], ['The old password is incorrect.'])

    def test_password_update_with_non_matching_new_passwords(self):
        """
        TUF11: Test updating the password with non-matching new passwords.
        """
        form_data = {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!'
        }
        form = UpdatePasswordForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
        self.assertEqual(form.errors['new_password2'], ['The new passwords do not match.'])

    def test_password_update_with_new_password_same_as_old_password(self):
        """
        TUF12: Test updating the password with the new password same as the old password.
        """
        form_data = {
            'old_password': 'Password123!',
            'new_password1': 'Password123!',
            'new_password2': 'Password123!'
        }
        form = UpdatePasswordForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertEqual(form.errors['new_password1'], ['The new password cannot be the same as the old password.'])

    def test_valid_description_update(self):
        """
        TUF13: Test updating the description with valid data.
        """
        form_data = {
            'description': 'This is a new description.'
        }
        form = UpdateDescriptionForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_account_deactivation_with_checkbox_checked(self):
        """
        TUF14: Test deactivating the account with the checkbox checked.
        """
        form_data = {
            'deactivate_profile': True
        }
        form = DeactivateAccountForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_account_deactivation_without_checkbox_checked(self):
        """
        TUF15: Test deactivating the account without checking the checkbox.
        """
        form_data = {
            'deactivate_profile': False
        }
        form = DeactivateAccountForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('deactivate_profile', form.errors)
        self.assertEqual(form.errors['deactivate_profile'], ['This field is required.'])

    def test_valid_flair_update(self):
        """
        TUF16: Test updating the flair with valid data.
        """
        form_data = {
            'flair': 'New Flair'
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertTrue(form.is_valid())

    def test_flair_update_with_empty_flair(self):
        """
        TUF17: Test updating the flair with an empty value.
        """
        form_data = {
            'flair': ''
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertFalse(form.is_valid())
        self.assertIn('flair', form.errors)

    def test_flair_update_with_flair_exceeding_max_length(self):
        """
        TUF18: Test updating the flair with a value exceeding max length.
        """
        form_data = {
            'flair': 'a' * 101
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertFalse(form.is_valid())
        self.assertIn('flair', form.errors)


class UpdateEmploymentsFormTest(TestCase):
    """
    Test case for the UpdateEmploymentsForm.
    """

    def setUp(self):
        """
        TUF19: Set up initial employment data for use in the tests.
        """
        self.employment_data = {
            'company': 'Test Company',
            'position': 'Software Engineer',
            'start_date': date.today() - timedelta(days=365),
            'end_date': date.today(),
        }

    def test_valid_form(self):
        """
        TUF20: Test form validation with valid data.
        """
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertTrue(form.is_valid())

    def test_missing_company(self):
        """
        TUF21: Test form validation with missing company field.
        """
        self.employment_data['company'] = ''
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['company'], ["Company field is required."])

    def test_missing_position(self):
        """
        TUF22: Test form validation with missing position field.
        """
        self.employment_data['position'] = ''
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['position'], ["Position field is required."])

    def test_missing_start_date(self):
        """
        TUF23: Test form validation with missing start date field.
        """
        self.employment_data['start_date'] = ''
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start_date'], ["Start date field is required."])

    def test_start_date_in_future(self):
        """
        TUF24: Test form validation with a start date set in the future.
        """
        self.employment_data['start_date'] = date.today() + timedelta(days=1)
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start_date'], ["Start date cannot be in the future."])

    def test_end_date_before_start_date(self):
        """
        TUF25: Test form validation with an end date before the start date.
        """
        self.employment_data['end_date'] = self.employment_data['start_date'] - timedelta(days=1)
        form = UpdateEmploymentsForm(data=self.employment_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['end_date'], ["End date cannot be before the start date."])


class UpdateEducationFormTest(TestCase):
    """
    Test case for the UpdateEducationForm.
    """

    def setUp(self):
        """
        TUF26: Set up initial education data for use in the tests.
        """
        self.education_data = {
            'school_name': 'Test University',
            'degree': 'Bachelor of Science',
            'start_date': date.today() - timedelta(days=365*4),
            'end_date': date.today(),
        }

    def test_valid_form(self):
        """
        TUF27: Test form validation with valid data.
        """
        form = UpdateEducationForm(data=self.education_data)
        self.assertTrue(form.is_valid())

    def test_missing_school_name(self):
        """
        TUF28: Test form validation with missing school name field.
        """
        self.education_data['school_name'] = ''
        form = UpdateEducationForm(data=self.education_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['school_name'], ["School name field is required."])

    def test_missing_degree(self):
        """
        TUF29: Test form validation with missing degree field.
        """
        self.education_data['degree'] = ''
        form = UpdateEducationForm(data=self.education_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['degree'], ["Degree field is required."])

    def test_missing_start_date(self):
        """
        TUF30: Test form validation with missing start date field.
        """
        self.education_data['start_date'] = ''
        form = UpdateEducationForm(data=self.education_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start_date'], ["Start date field is required."])

    def test_start_date_in_future(self):
        """
        TUF31: Test form validation with a start date set in the future.
        """
        self.education_data['start_date'] = date.today() + timedelta(days=1)
        form = UpdateEducationForm(data=self.education_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['start_date'], ["Start date cannot be set in the future."])

    def test_end_date_before_start_date(self):
        """
        TUF32: Test form validation with an end date before the start date.
        """
        self.education_data['end_date'] = self.education_data['start_date'] - timedelta(days=1)
        form = UpdateEducationForm(data=self.education_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['end_date'], ["End date cannot be before the start date."])


class BanFormTest(TestCase):
    """
    Test case for the BanForm.
    """

    def setUp(self):
        """
        TUF33: Set up a test user for use in the tests.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='Password123!',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )

    def test_valid_ban_form(self):
        """
        TUF34: Test form validation with valid data.
        """
        form = BanForm(data={'reason_banned': 'Violation of terms', 'confirm_ban': True}, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_missing_reason_banned(self):
        """
        TUF35: Test form validation with missing reason for banning.
        """
        form = BanForm(data={'confirm_ban': True}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['reason_banned'], ["You must provide a reason for banning the user."])

    def test_missing_confirm_ban(self):
        """
        TUF36: Test form validation with missing confirmation for ban.
        """
        form = BanForm(data={'reason_banned': 'Violation of terms'}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['confirm_ban'], ["You must confirm you want to ban the user."])

    def test_already_banned_user(self):
        """
        TUF37: Test form validation for already banned user.
        """
        self.user.is_banned = True
        self.user.save()
        form = BanForm(data={'reason_banned': 'Violation of terms', 'confirm_ban': True}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['This user is already banned.'])

    def test_ban_admin_user(self):
        """
        TUF38: Test form validation for banning an admin user.
        """
        self.user.is_superuser = True
        self.user.save()
        form = BanForm(data={'reason_banned': 'Violation of terms', 'confirm_ban': True}, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.non_field_errors(), ['You can\'t ban an admin.'])

    def test_save_banned_user(self):
        """
        TUF39: Test saving a banned user.
        """
        form = BanForm(data={'reason_banned': 'Violation of terms', 'confirm_ban': True}, instance=self.user)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.is_banned)




if __name__ == '__main__':
    unittest.main()