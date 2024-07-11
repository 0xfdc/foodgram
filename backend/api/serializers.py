import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Tag, Ingridient

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        model = User
        required_fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        required_fields = (
            'email', 'username', 'first_name', 'last_name', 'password'
        )
        model = User


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'avatar'
        )
        model = User


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        fields = ('avatar',)
        model = User
        required_fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingridient
