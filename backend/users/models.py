from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram_backend import constants
from users.validators import UsernameValidator


class FoodgramUser(AbstractUser):
    username = models.CharField(
        'Ник пользователя',
        max_length=constants.USER_TEXTFIELD_MAX_LENGTH,
        unique=True,
        validators=[
            UsernameValidator()
        ]
    )
    first_name = models.CharField(
        'Имя', max_length=constants.USER_TEXTFIELD_MAX_LENGTH, blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=constants.USER_TEXTFIELD_MAX_LENGTH,
        blank=False
    )
    email = models.EmailField(
        'E-mail',
        blank=False,
        unique=True
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE,
                             related_name='subscriptions')
    subscription = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE,
                                     related_name='subscribers')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='unique_subscribe'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('subscription')),
                name='self_subscribe_prevent'
            )
        ]
