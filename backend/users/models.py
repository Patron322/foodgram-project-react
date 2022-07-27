from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class UserRole():
    USER = 'user'
    ADMIN = 'admin'
    GUEST = 'guest'
    CHOICES = [
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (GUEST, 'Гость'),
    ]


class User(AbstractUser):

    role = models.CharField(
        max_length=5,
        choices=UserRole.CHOICES,
        default=UserRole.USER,
        verbose_name='Роль пользователя'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Логин',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
            ),
        ]
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        unique=True
    )

    @property
    def allowed_role(self):
        return self.role == UserRole.USER or self.role == UserRole.ADMIN

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
