from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField('Название', max_length=settings.TAG_MAX_LENGTH,
                            blank=False, unique=True)
    slug = models.SlugField(max_length=settings.TAG_MAX_LENGTH, blank=False,
                            unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Ingridient(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.INGRIDIENT_NAME_MAX_LENGTH,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MEASUREMENT_UNIT_MAX_LENGTH,
        blank=False
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
