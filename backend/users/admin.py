from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser


class FoodgramUserAdmin(UserAdmin):
    search_fields = ('username', 'email')


admin.site.register(FoodgramUser, FoodgramUserAdmin)
