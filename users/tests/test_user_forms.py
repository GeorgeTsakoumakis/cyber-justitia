import unittest

from django.test import TestCase
from users.forms import UpdateDetailsForm, UpdatePasswordForm, UpdateDescriptionForm, DeactivateAccountForm, UpdateFlairForm
from users.models import CustomUser, ProfessionalUser


class UserFormTests(TestCase):
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

    def test_valid_user_details_update(self):
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_user_details_update_with_empty_first_name(self):
        form_data = {
            'first_name': '',
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_user_details_update_with_empty_last_name(self):
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': '',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_user_details_update_with_empty_email(self):
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'NewLastName',
            'email': ''
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_details_update_with_first_name_exceeding_max_length(self):
        form_data = {
            'first_name': 'a' * 151,
            'last_name': 'NewLastName',
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_user_details_update_with_last_name_exceeding_max_length(self):
        form_data = {
            'first_name': 'NewFirstName',
            'last_name': 'a' * 151,
            'email': 'newemail@example.com'
        }
        form = UpdateDetailsForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_user_details_update_with_duplicate_email(self):
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
        form_data = {
            'old_password': 'Password123!',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        form = UpdatePasswordForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_password_update_with_incorrect_old_password(self):
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
        form_data = {
            'description': 'This is a new description.'
        }
        form = UpdateDescriptionForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_account_deactivation_with_checkbox_checked(self):
        form_data = {
            'deactivate_profile': True
        }
        form = DeactivateAccountForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_account_deactivation_without_checkbox_checked(self):
        form_data = {
            'deactivate_profile': False
        }
        form = DeactivateAccountForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('deactivate_profile', form.errors)
        self.assertEqual(form.errors['deactivate_profile'], ['This field is required.'])

    def test_valid_flair_update(self):
        form_data = {
            'flair': 'New Flair'
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertTrue(form.is_valid())

    def test_flair_update_with_empty_flair(self):
        form_data = {
            'flair': ''
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertFalse(form.is_valid())
        self.assertIn('flair', form.errors)

    def test_flair_update_with_flair_exceeding_max_length(self):
        form_data = {
            'flair': 'a' * 101
        }
        form = UpdateFlairForm(data=form_data, instance=self.professional_user)
        self.assertFalse(form.is_valid())
        self.assertIn('flair', form.errors)


if __name__ == '__main__':
    unittest.main()