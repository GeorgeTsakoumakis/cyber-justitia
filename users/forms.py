from django import forms
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


class UpdateDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]

    def clean_email(self):
        # Check if the email is already in use
        email = self.cleaned_data["email"]
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_("This email is already in use."), code="invalid")
        return email


class UpdatePasswordForm(forms.ModelForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        )
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="New password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Confirm new password",
    )

    class Meta:
        model = CustomUser
        fields = ["old_password", "new_password1", "new_password2"]

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        # Check if the old password is correct
        if not self.instance.check_password(old_password):
            raise forms.ValidationError("The old password is incorrect.")

        # Check if the new passwords match
        if new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        # Check if the new password is the same as the old password
        if old_password == new_password1:
            raise forms.ValidationError(
                "The new password cannot be the same as the old password."
            )
        return cleaned_data


class UpdateDescriptionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["description"]



class DeactivateAccountForm(forms.ModelForm):
    deactivate_profile = forms.BooleanField(
        required=True,
        initial=False,
        widget=forms.CheckboxInput()

    )

    class Meta:
        model = CustomUser
        fields = []
