import re

from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_password(value):
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if len(value) > 128:
        raise ValidationError('Password must be at most 128 characters long.')
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one digit.')

def validate_username(value):
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters long.')
    if len(value) > 30:
        raise ValidationError('Username must be at most 30 characters long.')
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError('Username can only contain letters, numbers, and underscores.')

def validate_birth_year(value):
    if value < 1900 or value > timezone.now().year:
        raise ValidationError('Birth year must be between 1900 and the current year.')

def validate_height_cm(value):
    if value < 50 or value > 300:
        raise ValidationError('Height must be between 50 cm and 300 cm.')

def validate_weight_kg(value):
    if value < 20 or value > 500:
        raise ValidationError('Weight must be between 20 kg and 500 kg.')