import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class NumberValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("Das Passwort muss mindestens eine Ziffer enthalten: 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Das Passwort muss mindestens eine Ziffer enthalten: 0-9."
        )


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("Das Passwort muss mindestens einen Großbuchstaben enthalten: A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Das Passwort muss mindestens einen Großbuchstaben enthalten: A-Z."
        )


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("Das Passwort muss mindestens einen Kleinbuchstaben enthalten: a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "Das Passwort muss mindestens einen Kleinbuchstaben enthalten: a-z."
        )


class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}`~@#$%^&*_?!]', password):
            raise ValidationError(
                _("Das Passwort muss mindestens ein Sonderzeichen enthalten: " +
                  "()[]{}`~@#$%^&*_?!"),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            "Das Passwort muss mindestens ein Sonderzeichen enthalten: " +
            "()[]{}`~@#$%^&*_?!"
        )

class NotAllowedValidator(object):
    def validate(self, password, user=None):
        if re.findall('[^a-zA-Z0-9()[\]{}`~@#$%^&*_?!]', password):
            raise ValidationError(
                _("Das Passwort darf nur a-z, A-Z, 0-9 und die folgenden Sonderzeichen enthalten: " +
                  "()[]{}`~@#$%^&*_?!"),
                code='password_not_allowed',
            )

    def get_help_text(self):
        return _(
            "Das Passwort darf keine anderen Symbole enthalten."
        )