from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewset
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.serializers import (AvatarSerializer, TagSerializer,
                             IngridientSerializer)
from api.viewsets import TagsIngridientsMixViewSet
from recipes.models import Tag, Ingridient

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
            http_status = status.HTTP_200_OK
            return Response(serializer.validated_data, status=http_status)
        else:
            http_status = status.HTTP_400_BAD_REQUEST
            error = {'avatar': ["Обязательное поле."]}
            return Response(error, status=http_status)

    def delete(self, request):
        user = User.objects.get(username=request.user)
        serializer = AvatarSerializer(user, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(avatar=None)
        http_status = status.HTTP_204_NO_CONTENT
        return Response(status=http_status)


class UserViewSet(DjoserUserViewset):
    http_method_names = ('get', 'post')

    def reset_username_confirm(self, request, *args, **kwargs):
        pass

    def reset_username(self, request, *args, **kwargs):
        pass

    def set_username(self, request, *args, **kwargs):
        pass

    def reset_password_confirm(self, request, *args, **kwargs):
        pass

    def reset_password(self, request, *args, **kwargs):
        pass

    def resend_activation(self, request, *args, **kwargs):
        pass

    def activation(self, request, *args, **kwargs):
        pass


class TagsViewSet(TagsIngridientsMixViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngridientViewSet(TagsIngridientsMixViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngridientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'name': ['istartswith'],
    }
