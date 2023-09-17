from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
      verbose_name='Адрес электронной почты',
      max_length=254,
      unique=True,
      blank=False,
      )

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True,
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True,
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
    )

    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    def __str__(self):
        return f'{self.username}: {self.email}'

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.is_superuser or self.role == settings.ADMIN
                or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == settings.MODERATOR


class Subscription(models.Model):

    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscribes',
        to=User,
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        verbose_name='Подписчики',
        related_name='subscribers',
        to=User,
        on_delete=models.CASCADE,
    )

    data_added = models.DateField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    def __str__(self):
        return f'{self.user.username}: {self.author.username}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
