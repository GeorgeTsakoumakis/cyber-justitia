from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "users"

    first_name = models.CharField(_("first name"), max_length=150, blank=False, null=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False, null=False)
    description = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="A short description about yourself",
    )
    is_banned = models.BooleanField(default=False)

    reason_banned = models.CharField(
        _("reason for getting banned"),
        max_length=150,
        null=True,
        blank=True,
        help_text="Reason for banning this user",
    )

    email = models.EmailField(
        _("email address"), null=False, blank=False, unique=True, max_length=320
    )

    def clean(self):
        # Updated clean function because default Django doesn't recognize whitespace as blank
        super().clean()
        if not self.first_name.strip():
            raise ValidationError({'first_name': "First name cannot be blank or whitespace only."})
        if not self.last_name.strip():
            raise ValidationError({'last_name': "Last name cannot be blank or whitespace only."})

    def __str__(self):
        return self.username

    @property
    def is_professional(self):
        """
        Check if the user is a professional user
        :return:  bool
        """
        # Query the ProfessionalUser model to check if the user is a professional
        exists = ProfessionalUser.objects.filter(user=self).exists()
        return exists

    # If user exists in professional user model, return its flair
    @property
    def flair(self):
        if self.is_professional:
            return ProfessionalUser.objects.get(user=self).flair
        return None


class ProfessionalUser(models.Model):
    class Meta:
        verbose_name = "Professional User"
        verbose_name_plural = "Professional Users"
        db_table = "professionals"

    prof_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    flair = models.CharField(
        _("professional flair"),
        max_length=100,
        null=False,
        help_text="Short text that best describes your professional skills",
    )


class Employments(models.Model):
    class Meta:
        db_table = "employments"
        verbose_name = "Employment"
        verbose_name_plural = "Employments"

    employment_id = models.AutoField(primary_key=True)
    prof_id = models.ForeignKey(
        ProfessionalUser, on_delete=models.CASCADE, related_name="employments"
    )
    company = models.CharField(_("company"), max_length=100, null=False)
    position = models.CharField(_("position"), max_length=100, null=False)
    start_date = models.DateField(_("start date"), null=False)
    end_date = models.DateField(_("end date"), null=True, blank=True)

    def clean_company(self):
        company = self.cleaned_data["company"]
        if not company:
            raise ValidationError(_("Company field is required."), code="invalid")
        if len(company) > 100:
            raise ValidationError(_("Company is too long."), code="invalid")
        return company

    def clean_position(self):
        position = self.cleaned_data["position"]
        if not position:
            raise ValidationError(_("Position field is required."), code="invalid")
        if len(position) > 100:
            raise ValidationError(_("Position is too long."), code="invalid")
        return position

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if not start_date:
            raise ValidationError(_("Start date field is required."), code="invalid")
        if start_date > datetime.date.today():
            raise ValidationError(
                _("Start date cannot be in the future."), code="invalid"
            )
        return start_date


class Education(models.Model):
    class Meta:
        db_table = "educations"
        verbose_name = "Education"
        verbose_name_plural = "Educations"

    education_id = models.AutoField(primary_key=True)
    prof_id = models.ForeignKey(
        ProfessionalUser, on_delete=models.CASCADE, related_name="educations"
    )
    school_name = models.CharField(_("institution"), max_length=100, null=False)
    degree = models.CharField(_("degree"), max_length=100, null=False)
    start_date = models.DateField(_("start date"), null=False)
    end_date = models.DateField(_("end date"), null=True, blank=True)

    def clean_school_name(self):
        school_name = self.cleaned_data["school_name"]
        if not school_name:
            raise ValidationError(_("School name field is required."), code="invalid")
        if len(school_name) > 100:
            raise ValidationError(_("School name is too long."), code="invalid")
        return school_name

    def clean_degree(self):
        degree = self.cleaned_data["degree"]
        if not degree:
            raise ValidationError(_("Degree field is required."), code="invalid")
        if len(degree) > 100:
            raise ValidationError(_("Degree is too long."), code="invalid")
        return degree

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if not start_date:
            raise ValidationError(_("Start date field is required."), code="invalid")
        if start_date > datetime.date.today():
            raise ValidationError(
                _("Start date cannot be in the future."), code="invalid"
            )
        return start_date
