import random

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram_backend import constants

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.TAG_MAX_LENGTH
    )
    slug = models.SlugField(max_length=constants.TAG_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=constants.MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            ),
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
    )
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        default=None
    )
    name = models.CharField(
        'Название',
        max_length=constants.RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                constants.MIN_COOKING_TIME,
                message=(
                    'Время приготовления должно быть не менее '
                    f'{constants.MIN_COOKING_TIME} минуты'
                )
            ),
            MaxValueValidator(
                constants.MAX_COOKING_TIME,
                message=(
                    'Время приготовления должно быть не более '
                    f'{constants.MAX_COOKING_TIME} минут'
                )
            )
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    hash = models.CharField(
        'Короткая ссылка',
        max_length=constants.SHORT_LINK_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name

    def generate_hash(self):
        storage = Recipe.objects.all().values_list(
            'hash', flat=True
        )
        population = [chr(i) for i in range(97, 122)]
        population.extend([chr(i) for i in range(65, 90)])
        hash = ''.join(random.choices(population, k=5))
        while hash in storage:
            hash = ''.join(random.choices(population, k=5))
        return hash

    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.generate_hash()
        return super().save(*args, **kwargs)


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                constants.MIN_INGREDIENT_VALUE,
                message=(
                    'Количество должно быть не меньше '
                    f'{constants.MIN_INGREDIENT_VALUE}'
                )
            ),
            MaxValueValidator(
                constants.MAX_INGREDIENT_VALUE,
                message=(
                    'Количество должно быть не больше '
                    f'{constants.MAX_INGREDIENT_VALUE}'
                )
            )
        ),
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        ]

    def __str__(self):
        return self.ingredient.name


class ShoppingCartFavorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )

    class Meta:
        abstract = True


class Favorite(ShoppingCartFavorite):

    class Meta:
        default_related_name = '%(app_label)s_%(class)s'
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        ]


class ShoppingCart(ShoppingCartFavorite):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = '%(app_label)s_%(class)s'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]
