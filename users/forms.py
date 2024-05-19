from django import forms
from .models import CustomUser


class UpdateDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']



class UpdatePasswordForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['password']


class UpdateDescriptionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['description']

class DeleteAccountForm(forms.ModelForm):
    delete_profile = forms.BooleanField(
        required=True,
        initial=False,
        widget=forms.CheckboxInput()
    )
    class Meta:
        model = CustomUser
        fields = []