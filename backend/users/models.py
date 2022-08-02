from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from .managers import UserManager


class User(AbstractUser, PermissionsMixin):

    password = models.CharField('Пароль', max_length=150)
    email = models.EmailField('E-mail', max_length=254, unique=True)
    username = models.CharField('Логин', max_length=150, unique=True)
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField('Фамилия', max_length=150)
    is_superuser = models.BooleanField('Администратор', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_superuser

    def get_full_name(self):
        return self.first_name, self.last_name

    def get_short_name(self):
        return self.first_name


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )

    class Meta:
        ordering = ['-pk']
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'], name='unique_subscriber'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('subscriber')),
                name='no_subcribe_self',
            ),
        ]
