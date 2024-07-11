from django.contrib import admin

from recipes.models import Tag


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
    model = Tag
    extra = 0


admin.site.register(Tag, TagAdmin)
