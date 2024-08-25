import io

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
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
                             FavoriteSerializer, CartSerializer)
from api.viewsets import (TagsIngredientsMixViewSet, ListViewSet)
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingCart,
                            RecipeIngredients)
from users.models import Subscription

User = get_user_model()


class AvatarView(APIView):
    serializer_class = AvatarSerializer
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = AvatarSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.to_representation(request.user),
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        serializer = AvatarSerializer(
            request.user,
            data={},
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewset):
    http_method_names = ('get', 'post', 'delete')

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        subscription_user = get_object_or_404(
            User, pk=id
        )
        subscribes_deleted, _ = Subscription.objects.filter(
            user=request.user.id, subscription=subscription_user.id
        ).delete()
        if not subscribes_deleted:
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        hash = get_object_or_404(Recipe, pk=pk).hash
        response = {
            'short-link': f'http://{request.META["HTTP_HOST"]}/s/{hash}/'
        }
        return Response(
            response,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        favorite_recipe = get_object_or_404(
            Recipe, pk=pk
        )
        favorite_deleted, _ = Favorite.objects.filter(
            user=request.user.id, recipe=favorite_recipe.id
        ).delete()
        if not favorite_deleted:
            return Response(
                {'errors': 'Такого рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        cart_recipe = get_object_or_404(
            Recipe, pk=pk
        )
        recipes_deleted, _ = ShoppingCart.objects.filter(
            user=request.user.id, recipe=cart_recipe.id
        ).delete()
        if not recipes_deleted:
            return Response(
                {'errors': 'Такого рецепта нет в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        pdf.setFont('DejaVuSerif', 14)
        ingredients = RecipeIngredients.objects.filter(
            recipe__recipes_shoppingcart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))
        for ingredient in ingredients:
            data = (
                f'{ingredient["ingredient__name"]} - {ingredient["sum"]} '
                f'{ingredient["ingredient__measurement_unit"]}'
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


def short_link_redirect(request, hash):
    recipe_id = get_object_or_404(
        Recipe,
        hash=hash
    ).id
    return HttpResponseRedirect(
        request.build_absolute_uri(f'/recipes/{recipe_id}/')
    )
