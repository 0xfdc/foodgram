from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeTags, RecipeIngredients, Tag


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
    )
    search_fields = ('name',)
    list_filter = ('tags',)
    list_display_links = ('name',)
    inlines = (TagInline, IngredientInline)

    def get_favorited(self, obj):
        return obj.favorite.count()
    get_favorited.short_description = 'Добавлений в избранное'


class RecipeInLine(admin.StackedInline):
    model = Recipe
    extra = 0


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
