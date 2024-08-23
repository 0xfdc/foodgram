import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            RecipeTags, Tag, ShoppingCart)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CreateUserSerializer(UserCreateSerializer):

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')
        required_fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )
        model = User


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'avatar'
        )
        model = User

    def get_is_subscribed(self, obj):
        if (
            'request' not in self.context or
            self.context['request'].user.is_anonymous
        ):
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user, subscription=obj
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        fields = ('avatar',)
        model = User
        required_fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag
        read_only_fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredients.objects.all(),
                fields=('recipe', 'ingredient')
            )
        ]


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'subscription')
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscription'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]

    def validate_subscription(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError('Нельзя подписываться на себя!')
        return value


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном.'
            )
        ]


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('user', 'recipe')
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в списке покупок.'
            )
        ]


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'is_subscribed',
                  'recipes', 'recipes_count', 'last_name', 'avatar')
        model = User

    def get_is_subscribed(self, obj):
        subscriptions_list = obj.subscriptions.values_list(
            'subscription', flat=True
        )
        return self.context['request'].user.id in subscriptions_list

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(
            recipe_id=obj.id
        )
        return RecipeIngredientsSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        favorite_list = (
            self.context['request'].user.favorite.values_list(
                'recipe', flat=True
            )
        )
        return obj.id in favorite_list

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        cart_list = (
            self.context['request'].user.shopping_cart.values_list(
                'recipe', flat=True
            )
        )
        return obj.id in cart_list


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    author = UserListSerializer(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientSerializer(many=True)

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')
        model = Recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeListSerializer(instance,
                                          context={'request': request})
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент'
            )
        elif not tags:
            raise serializers.ValidationError(
                'Рецепт должен быть связан хотя бы с одним тегом'
            )
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTags.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if not ingredients:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы один ингредиент'
            )
        elif not tags:
            raise serializers.ValidationError(
                'Рецепт должен быть связан хотя бы с одним тегом'
            )
        new_instance = super().update(instance, validated_data)
        RecipeTags.objects.filter(recipe=new_instance).delete()
        RecipeIngredients.objects.filter(recipe=new_instance).delete()
        for tag in tags:
            RecipeTags.objects.create(recipe=new_instance, tag=tag)
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=new_instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return new_instance

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if ingredients:
            ingredient_ids = list()
            for ingredient in ingredients:
                if ingredient.get('id') in ingredient_ids:
                    raise serializers.ValidationError(
                        'Ингредиенты не должны повторяться'
                    )
                ingredient_ids.append(ingredient.get('id'))
        if tags:
            tag_ids = list()
            for tag in tags:
                if tag in tag_ids:
                    raise serializers.ValidationError(
                        'Теги не должны повторяться'
                    )
                tag_ids.append(tag)
        return data
