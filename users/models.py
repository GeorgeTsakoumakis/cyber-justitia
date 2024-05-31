from datetime import date
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

    def clean(self):
        super().clean()
        if not self.flair:
            raise ValidationError(_("Flair field is required."), code="invalid")
        if len(self.flair) > 100:
            raise ValidationError(_("Flair is too long."), code="invalid")
        return self

    def __str__(self):
        return self.user.username


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

    def clean(self):
        super().clean()
        if not self.company:
            raise ValidationError(_("Company name field is required."), code="invalid")
        if len(self.company) > 100:
            raise ValidationError(_("Company name is too long."), code="invalid")
        if not self.position:
            raise ValidationError(_("Position field is required."), code="invalid")
        if len(self.position) > 100:
            raise ValidationError(_("Position name is too long."), code="invalid")
        if not self.start_date:
            raise ValidationError(_("Start date field is required."), code="invalid")
        if self.start_date > date.today():
            raise ValidationError(_("Start date cannot be in the future."), code="invalid")
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before the start date."), code="invalid")
        return self

    def __str__(self):
        return self.company + " - " + self.position


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

    def clean(self):
        super().clean()

        if not self.school_name:
            raise ValidationError(_("School name field is required."), code="invalid")
        if len(self.school_name) > 100:
            raise ValidationError(_("School name is too long."), code="invalid")

        if not self.degree:
            raise ValidationError(_("Degree field is required."), code="invalid")
        if len(self.degree) > 100:
            raise ValidationError(_("Degree name is too long."), code="invalid")

        if not self.start_date:
            raise ValidationError(_("Start date field is required."), code="invalid")
        if self.start_date > date.today():
            raise ValidationError(_("Start date cannot be in the future."), code="invalid")

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("End date cannot be before the start date."), code="invalid")

        return self

    def __str__(self):
        return self.school_name + " - " + self.degree