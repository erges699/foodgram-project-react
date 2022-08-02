from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_validator

USER = 'user'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Обязательное поле. 150 символов или меньше.'
            'Только буквы, цифры и @/./+/-/_'),
        validators=(username_validator,),
        error_messages={
             'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
    )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField(
        'О себе',
        blank=True,
        help_text='Расскажите немного о себе.'
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role[0]) for role in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        help_text=(
            'Роль пользователя на ресурсе.'
            'User или Admin'
            'Изменить роль может только Admin'
        )
    )
    confirmation_code = models.CharField(
        max_length=20,
    )

    class Meta:
        ordering = ('-username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff
