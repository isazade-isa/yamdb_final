from django.core.exceptions import ValidationError
from django.utils import timezone


def year_is_valid(value):
    if not (0 < value <= timezone.now().year):
        raise ValidationError('Не верный год указан!')
