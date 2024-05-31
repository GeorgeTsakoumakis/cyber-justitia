"""
This file is used to register the models in the admin panel.

Author: Georgios Tsakoumakis
"""

from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfessionalUser, Education, Employments


class CustomUserChangeForm(UserChangeForm):
    """
    Custom user change form that extends the default Django user change form.
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Custom user admin that extends the default Django user admin.
    """
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "description",
                    "flair",
                    "is_professional",
                    "is_banned",
                    "reason_banned",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProfessionalUser)
admin.site.register(Education)
admin.site.register(Employments)
