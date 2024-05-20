from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterPasswordValidator:
    def __init__(self, special_characters="~!@#$%^&*()_+{}\":;'[]"):
        self.special_characters = special_characters

    def validate(self, password, user=None):
        if not any(char in self.special_characters for char in password):
            raise ValidationError(
                _("This password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _("Your password must contain at least one special character.")