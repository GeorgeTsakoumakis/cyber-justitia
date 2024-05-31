"""
Models for the users app
Author: Georgios Tsakoumakis, Jonathan Muse, Ionut-Valeriu Facaeru
"""

from datetime import date
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model
    Additional fields:
    - description: A short description about the user
    - is_banned: A boolean field that indicates if the user is banned
    - reason_banned: A short description about the reason for banning the user
    """
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
        """
        Custom clean method to validate the user model
        :raises ValidationError: If the first name or last name is empty or whitespace only
        :return: None
        """
        super().clean()
        if not self.first_name.strip():
            raise ValidationError({'first_name': "First name cannot be blank or whitespace only."})
        if not self.last_name.strip():
            raise ValidationError({'last_name': "Last name cannot be blank or whitespace only."})

    def __str__(self):
        """
        String representation of the user model
        :return: str - username
        """
        return self.username

    @property
    def is_professional(self):
        """
        Check if the user is a professional user
        :return: bool
        """
        # Query the ProfessionalUser model to check if the user is a professional
        exists = ProfessionalUser.objects.filter(user=self).exists()
        return exists

    @property
    def flair(self):
        """
        Get the flair of the professional user
        :return: str - flair
        """
        # If user exists in professional user model, return its flair
        if self.is_professional:
            return ProfessionalUser.objects.get(user=self).flair
        return None


class ProfessionalUser(models.Model):
    """
    Model to store information about professional users in conjunction with the CustomUser model
    Additional fields:
    - prof_id: Primary key field for professionals
    - user: One-to-one field to the CustomUser model
    - flair: A short text that best describes the professional qualifications of the user
    """
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
        help_text="Short text that best describes your professional qualifications",
    )

    def clean(self):
        """
        Custom clean method to validate the professional user model
        :raises ValidationError: If the flair is empty or longer than 100 characters
        :return: None
        """
        super().clean()
        if not self.flair:
            raise ValidationError(_("Flair field is required."), code="invalid")
        if len(self.flair) > 100:
            raise ValidationError(_("Flair is too long."), code="invalid")
        return self

    def __str__(self):
        """
        String representation of the professional user model
        :return: str - username
        """
        return self.user.username


class Employments(models.Model):
    """
    Model to store information about employment credentials of professional users
    Fields:
    - employment_id: Primary key field for employments
    - prof_id: Foreign key to the ProfessionalUser model (one-to-many relationship)
    - company: Name of the company where the user was employed
    - position: Position held by the user in the company
    - start_date: Start date of the employment
    - end_date: End date of the employment (optional)
    """
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
        """
        Custom clean method to validate the employment model
        :raises ValidationError: If the company, position or start date is empty or longer than 100 characters
        :raises ValidationError: If the start date is in the future or the end date is before the start date
        :return: None
        """
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
        """
        String representation of the employment model
        :return: str - company name and position
        """
        return self.company + " - " + self.position


class Education(models.Model):
    """
    Model to store information about education credentials of professional users
    Fields:
    - education_id: Primary key field for educations
    - prof_id: Foreign key to the ProfessionalUser model (one-to-many relationship)
    - school_name: Name of the institution where the user studied
    - degree: Degree obtained by the user
    - start_date: Start date of the education
    - end_date: End date of the education (optional)
    """
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
        """
        Custom clean method to validate the education model
        :raises ValidationError: If the school name, degree or start date is empty or longer than 100 characters
        :raises ValidationError: If the start date is in the future or the end date is before the start date
        :return: None
        """
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
        """
        String representation of the education model
        :return: str - school name and degree
        """
        return self.school_name + " - " + self.degree
