from django.contrib import admin

from recipes.models import (Ingredient, Recipe, RecipeIngredients, Tag,
                            Favorite, ShoppingCart)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class IngredientInline(admin.StackedInline):
    model = RecipeIngredients
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date'
    )
    search_fields = ('name',)
    list_filter = ('name', 'tags', 'author')
    list_display_links = ('name',)
    readonly_fields = ('favorited', 'pub_date')
    inlines = (IngredientInline,)

    def favorited(self, obj):
        return obj.recipes_favorite.count()
    favorited.short_description = 'Добавлений в избранное'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('user',)
    search_fields = ('user',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
