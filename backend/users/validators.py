import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


class UsernameValidator(UnicodeUsernameValidator):
    message = (
        '\'username\' содержит запрещенные символы: %(invalid_chars)s.'
    )

    def __call__(self, value):
        regex_matches = self.regex.search(str(value))
        invalid_input = not regex_matches
        if invalid_input:
            invalid_chars = set(re.sub(r'[\w.@+-]+', '', str(value)))
            raise ValidationError(
                self.message,
                code=self.code,
                params={'invalid_chars': invalid_chars}
            )


class NotMeUsernameValidator(RegexValidator):
    regex = r'^me\Z'
    message = (
        'Запрещено использовать \'me\' в качестве \'username\'.'
    )
    flags = 0
    inverse_match = True
