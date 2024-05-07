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
    is_banned = models.BooleanField(default=False)

    email = models.EmailField(_("email address"), null=False, blank=False, unique=True, max_length=320)

    def __str__(self):
        return self.username


class ProfessionalUser(models.Model):
    class Meta:
        verbose_name = 'Professional User'
        verbose_name_plural = 'Professional Users'
        db_table = 'professionals'

    prof_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    flair = models.CharField(max_length=100, null=False, help_text="Short text that best describes your "
                                                                  "professional skills")