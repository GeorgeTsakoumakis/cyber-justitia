"""
Test cases for user-related forms.

Author: Ionut-Valeriu Facaeru, Georgios Tsakoumakis
"""

import unittest
from django.test import TestCase
from users.forms import UpdateDetailsForm, UpdatePasswordForm, UpdateDescriptionForm, DeactivateAccountForm, UpdateFlairForm
from users.models import CustomUser, ProfessionalUser


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


if __name__ == '__main__':
    unittest.main()