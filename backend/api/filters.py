from django_filters.rest_framework import (
    ModelMultipleChoiceFilter, FilterSet, BooleanFilter
)

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    is_favorited = BooleanFilter(
        method='filter_by_is_favorited', label='Favorite'
    )

    is_in_shopping_cart = BooleanFilter(
        method='filter_by_is_in_shopping_cart', label='In shopping cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_by_is_favorited(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                favorite__user_id=self.request.user.id
            )
        else:
            queryset = queryset.exclude(
                favorite__user_id=self.request.user.id
            )
        return queryset

    def filter_by_is_in_shopping_cart(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                shoppingcart__user_id=self.request.user.id
            )
        else:
            queryset = queryset.exclude(
                shoppingcart__user_id=self.request.user.id
            )
        return queryset
