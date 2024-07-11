from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import AvatarView, UserViewSet, TagsViewSet, IngridientViewSet

app_name = 'api'
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingridients', IngridientViewSet, basename='ingridients')


urlpatterns = [
    path('users/me/avatar/', AvatarView.as_view(), name='avatar_change'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
