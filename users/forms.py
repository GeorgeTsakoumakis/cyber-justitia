from datetime import timezone
from django import forms
from .models import CustomUser, ProfessionalUser, Education, Employments
from django.utils.translation import gettext_lazy as _


class UpdateDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email"]

    first_name = forms.CharField(
        label=_("First name"),
        max_length=150,
        error_messages={
            "required": _("First name field is required."),
            "max_length": _("First name is too long."),
        },
    )

    last_name = forms.CharField(
        label=_("Last name"),
        max_length=150,
        error_messages={
            "required": _("Last name field is required."),
            "max_length": _("Last name is too long."),
        },
    )

    email = forms.EmailField(
        label=_("Email address"),
        max_length=320,
        error_messages={
            "required": _("Email field is required."),
            "invalid": _("Invalid email address."),
        },
    )

    def clean_email(self):
        # Check if the email is already in use
        email = self.cleaned_data["email"]
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                _("This email is already in use."), code="invalid"
            )
        return email

    def clean_first_name(self):
        # Check if the first name is empty
        first_name = self.cleaned_data["first_name"]
        if not first_name:
            raise forms.ValidationError(
                _("First name field is required."), code="invalid"
            )
        # Check if the first name is too long
        if len(first_name) > 150:
            raise forms.ValidationError(_("First name is too long."), code="invalid")
        return first_name

    def clean_last_name(self):
        # Check if the last name is empty
        last_name = self.cleaned_data["last_name"]
        if not last_name:
            raise forms.ValidationError(
                _("Last name field is required."), code="invalid"
            )
        # Check if the last name is too long
        if len(last_name) > 150:
            raise forms.ValidationError(_("Last name is too long."), code="invalid")
        return last_name


class UpdatePasswordForm(forms.ModelForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "autofocus": True}
        ),
        error_messages={
            "required": _("Old password field is required."),
            "invalid": _("Invalid old password."),
        },
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="New password",
        error_messages={
            "required": _("New password field is required."),
            "invalid": _("Invalid new password."),
        },
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        label="Confirm new password",
        error_messages={
            "required": _("Confirm new password field is required."),
            "invalid": _("Invalid new password."),
        },
    )

    class Meta:
        model = CustomUser
        fields = ["old_password", "new_password1", "new_password2"]

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")

        # Check if the old password is correct
        if not self.instance.check_password(old_password):
            raise forms.ValidationError("The old password is incorrect.")

        return old_password

    def clean_new_password1(self):
        old_password = self.cleaned_data.get("old_password")
        new_password1 = self.cleaned_data.get("new_password1")

        # Check if the new password is the same as the old password
        if old_password and new_password1 == old_password:
            raise forms.ValidationError(
                "The new password cannot be the same as the old password."
            )

        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        # Check if the new passwords match
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        return new_password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


class UpdateDescriptionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["description"]


class DeactivateAccountForm(forms.ModelForm):
    deactivate_profile = forms.BooleanField(
        required=True, initial=False, widget=forms.CheckboxInput()
    )

    class Meta:
        model = CustomUser
        fields = []


class UpdateFlairForm(forms.ModelForm):
    class Meta:
        model = ProfessionalUser
        fields = ["flair"]
        error_messages = {
            "flair": {
                "required": "Flair field is required.",
                "invalid": "Invalid input.",
            },
        }

    def clean_flair(self):
        # Check if the flair is empty
        flair = self.cleaned_data["flair"]
        if not flair:
            raise forms.ValidationError(_("Flair field is required."), code="invalid")
        # Check if the flair is too long
        if len(flair) > 100:
            raise forms.ValidationError(_("Flair is too long."), code="invalid")
        return flair


class UpdateEmploymentsFrom(forms.ModelForm):
    class Meta:
        model = Employments
        fields = ["company", "position", "start_date", "end_date"]
        error_messages = {
            "company": {
                "required": "Company field is required.",
                "invalid": "Invalid input.",
            },
            "position": {
                "required": "Position field is required.",
                "invalid": "Invalid input.",
            },
            "start_date": {
                "required": "Start date field is required.",
                "invalid": "Invalid input.",
            },
        }

    def clean_company(self):
        company = self.cleaned_data["company"]
        if not company:
            raise forms.ValidationError(_("Company field is required."), code="invalid")
        return company

    def clean_employments(self):
        employments = self.cleaned_data["employments"]
        if not employments:
            raise forms.ValidationError(
                _("Employments field is required."), code="invalid"
            )
        return employments

    def clean_position(self):
        position = self.cleaned_data["position"]
        if not position:
            raise forms.ValidationError(
                _("Position field is required."), code="invalid"
            )
        return position

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if not start_date:
            raise forms.ValidationError(
                _("Start date field is required."), code="invalid"
            )
        if start_date > timezone.now().date():
                raise forms.ValidationError(
                    _("Start date cannot be set in the future."), code="invalid"
                )
        return start_date


class UpdateEducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ["school_name", "degree", "start_date", "end_date"]
        error_messages = {
            "school_name": {
                "required": "School name field is required.",
                "invalid": "Invalid input.",
            },
            "degree": {
                "required": "Degree field is required.",
                "invalid": "Invalid input.",
            },
            "start_date": {
                "required": "Start date field is required.",
                "invalid": "Invalid input.",
            },
        }

        school_name = forms.CharField(
            label=_("School name"),
            max_length=100,
            error_messages={
                "required": _("School name field is required."),
                "max_length": _("School name is too long."),
            },
        )

        degree = forms.CharField(
            label=_("Degree"),
            max_length=100,
            error_messages={
                "required": _("Degree field is required."),
                "max_length": _("Degree is too long."),
            },
        )

        start_date = forms.DateField(
            label=_("Start date"),
            error_messages={
                "required": _("Start date field is required."),
            },
        )

    def clean_school_name(self):
        school_name = self.cleaned_data["school_name"]
        if not school_name:
            raise forms.ValidationError(
                _("School name field is required"), code="invalid"
            )
        return school_name

    def clean_degree(self):
        degree = self.cleaned_data["degree"]
        if not degree:
            raise forms.ValidationError(_("Degree field is required"), code="invalid")
        return degree

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if not start_date:
            raise forms.ValidationError(_("Start date is required"), code="invalid")
        if start_date > timezone.now().date():
                raise forms.ValidationError(
                    _("Start date cannot be set in the future."), code="invalid"
                )
        return start_date


class BanForm(forms.ModelForm):
    """
    Form for banning a user.
    Renders a textarea for the reason for banning the user and a checkbox to confirm the ban.
    """
    class Meta:
        model = CustomUser
        fields = ["reason_banned"]
        widgets = {
            "reason_banned": forms.Textarea(attrs={"placeholder": "Reason for banning"}),
        }
        error_messages = {
            "reason_banned": {
                "required": "Reason field is required.",
                "invalid": "Invalid input.",
            },
        }

    confirm_ban = forms.BooleanField(
        required=True,
        label="Confirm ban",
        error_messages={
            "required": "You must confirm you want to ban the user.",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        reason_banned = cleaned_data.get('reason_banned')

        if not reason_banned:
            self.add_error('reason_banned', _('You must provide a reason for banning the user.'))

        # Can't ban an already banned user
        if self.instance.is_banned:
            self.add_error(None, 'This user is already banned.')

        # Can't ban an admin
        if self.instance.is_superuser:
            self.add_error(None, 'You can\'t ban an admin.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('confirm_ban'):
            user.is_banned = True
            if commit:
                user.save()
        return user
