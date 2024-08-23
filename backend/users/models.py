from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import UsernameValidator, NotMeUsernameValidator


class FoodgramUser(AbstractUser):
    username = models.CharField(
        'Ник пользователя',
        max_length=settings.USER_TEXTFIELD_MAX_LENGTH,
        unique=True,
        validators=[
            UsernameValidator(),
            NotMeUsernameValidator()
        ]
    )
    first_name = models.CharField(
        'Имя', max_length=settings.USER_TEXTFIELD_MAX_LENGTH, blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USER_TEXTFIELD_MAX_LENGTH,
        blank=False
    )
    email = models.EmailField(
        'E-mail',
        max_length=settings.EMAIL_MAX_LENGTH,
        blank=False,
        unique=True
    )
    avatar = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )

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
