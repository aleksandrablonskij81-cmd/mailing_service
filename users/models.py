from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с email как логином"""
    email = models.EmailField(unique=True, verbose_name='Email')
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='Email подтверждён'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email