import io

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet as DjoserUserViewset
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAdminOrOwnerOrReadOnly
from api.serializers import (AvatarSerializer, TagSerializer,
                             IngredientSerializer, RecipeSerializer,
                             UserSubscriptionsSerializer, SubscribeSerializer,
                             FavoriteSerializer, RecipeMinifiedSerializer,
                             CartSerializer)
from api.viewsets import (TagsIngredientsMixViewSet, ListViewSet)
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import Subscription

User = get_user_model()


class AvatarView(APIView):
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = User.objects.get(username=request.user)
        if ('avatar' in request.data):
            serializer = AvatarSerializer(user, data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.to_representation(user),
                status=status.HTTP_200_OK
            )
        else:
            http_status = status.HTTP_400_BAD_REQUEST
            error = {'avatar': ["Обязательное поле."]}
            return Response(error, status=http_status)

    def delete(self, request):
        user = User.objects.get(username=request.user)
        serializer = AvatarSerializer(user, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewset):
    http_method_names = ('get', 'post', 'delete')

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            subscription = get_object_or_404(User, pk=id)
            serializer = SubscribeSerializer(
                data={
                    'user': self.request.user.id,
                    'subscription': subscription.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            subscription_serializer = UserSubscriptionsSerializer(
                subscription,
                context={'request': request}
            )
            return Response(
                subscription_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            subscription_user = get_object_or_404(
                User, pk=id
            )
            subscription = Subscription.objects.filter(
                user=request.user.id, subscription=subscription_user.id
            )
            if not subscription.exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionListViewSet(ListViewSet):
    serializer_class = UserSubscriptionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        subscriptions_list = self.request.user.subscriptions.values_list(
            'subscription', flat=True
        )
        queryset = User.objects.filter(
            id__in=subscriptions_list
        )
        return queryset


class TagsViewSet(TagsIngredientsMixViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(TagsIngredientsMixViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_name='get-link',
            url_path='get-link')
    def getlink(self, request, pk=None):
        response = {
            'short-link': f'https://{request.META["HTTP_HOST"]}/s/{pk}/'
        }
        return Response(
            response,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = FavoriteSerializer(
                data={
                    'user': self.request.user.id,
                    'recipe': recipe.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            favorite_recipe = get_object_or_404(
                Recipe, pk=pk
            )
            favorite = Favorite.objects.filter(
                user=request.user.id, recipe=favorite_recipe.id
            )
            if not favorite.exists():
                return Response(
                    {'errors': 'Такого рецепта нет в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            recipe = get_object_or_404(Recipe, pk=pk)
            serializer = CartSerializer(
                data={
                    'user': self.request.user.id,
                    'recipe': recipe.id
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            cart_serializer = RecipeMinifiedSerializer(recipe)
            return Response(
                cart_serializer.data, status=status.HTTP_201_CREATED
            )
        else:
            cart_recipe = get_object_or_404(
                Recipe, pk=pk
            )
            cart = ShoppingCart.objects.filter(
                user=request.user.id, recipe=cart_recipe.id
            )
            if not cart.exists():
                return Response(
                    {'errors': 'Такого рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        PAGE_HEIGHT_DECREMENT = 20
        current_height = defaultPageSize[1] - PAGE_HEIGHT_DECREMENT
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        pdfmetrics.registerFont(
            TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8')
        )
        pdf.setFont("DejaVuSerif", 14)
        cart_recipes = request.user.shopping_cart.all()
        for cart_recipe in cart_recipes:
            ingredients = RecipeSerializer(
                Recipe.objects.get(pk=cart_recipe.recipe_id),
                context={'request': request}
            ).data['ingredients']
            ingredients_data = dict()
            for ingredient in ingredients:
                if ingredients_data[ingredient["name"]]:
                    ingredients_data[
                        ingredient["name"]
                    ]["amount"] += ingredient["amount"]
                else:
                    ingredients_data[ingredient["name"]] = {
                        'amount': ingredient["amount"],
                        'unit': ingredient["measurement_unit"]
                    }
            for ingredient in ingredients_data.keys():
                data = (
                    f'{ingredient} - {ingredients_data[ingredient]["amount"]} '
                    f'{ingredients_data[ingredient]["unit"]}'
                )
                current_height -= PAGE_HEIGHT_DECREMENT
                pdf.drawString(
                    40,
                    current_height,
                    data.encode('utf-8')
                )
        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )


def short_link_redirect(request, pk):
    return redirect('api:recipes-detail', pk=pk)
