from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscription


class FoodgramUserAdmin(UserAdmin):
    search_fields = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscription')
    list_display_links = ('user',)
    search_fields = ('user',)


admin.site.register(FoodgramUser, FoodgramUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
