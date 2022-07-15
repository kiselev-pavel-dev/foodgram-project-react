from djoser.serializers import (
    UserCreateSerializer,
    UsernameSerializer,
    UserSerializer,
)
from requests import request
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Subscription, User


class UserSerializerList(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user.pk
        return Subscription.objects.filter(
            author=obj.pk, subscriber=current_user
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
