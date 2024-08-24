from django.contrib import admin

from recipes.models import (Ingredient, Recipe, RecipeTags, RecipeIngredients,
                            Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


class TagInline(admin.StackedInline):
    model = RecipeTags
    extra = 0


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
    inlines = (TagInline, IngredientInline)

    def favorited(self, obj):
        return obj.favorited.count()
    favorited.short_description = 'Добавлений в избранное'


class RecipeInLine(admin.StackedInline):
    model = Recipe
    extra = 0


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
