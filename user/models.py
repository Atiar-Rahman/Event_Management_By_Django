from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?\d{9,15}$', 'Enter a valid phone number.')]
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        default='defaults/profile-placeholder.jpg',
        blank=True
    )

    def __str__(self):
        return self.username
