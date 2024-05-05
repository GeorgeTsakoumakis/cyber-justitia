from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'

    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    description = models.TextField(max_length=256, null=True, blank=True,
                                   help_text="A short description about yourself")
    flair = models.CharField(max_length=100, null=True, help_text="Short text that best describes your "
                                                                                "professional skills")
    is_professional = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    phone = models.CharField(max_length=20,
                             null=True,
                             blank=True,
                             validators=[
                                 RegexValidator(
                                     regex=r'^\d{4}-\d{3}-\d{4}$',
                                     message="Phone number must be entered in the format: '9999-999-9999'."
                                 )
                             ])

    email = models.EmailField(_("email address"), null=False, blank=False, unique=True)

    def __str__(self):
        return self.username
