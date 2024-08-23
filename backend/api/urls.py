from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (AvatarView, UserViewSet, TagsViewSet, IngredientViewSet,
                       RecipeViewSet, SubscriptionListViewSet)

app_name = 'api'
router = DefaultRouter()
router.register('users/subscriptions', SubscriptionListViewSet,
                basename='subscriptions')
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/me/avatar/', AvatarView.as_view(), name='avatar_change'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
