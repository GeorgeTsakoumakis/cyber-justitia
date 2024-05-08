from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ProfessionalUser


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
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
                    "phone",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ProfessionalUser)
