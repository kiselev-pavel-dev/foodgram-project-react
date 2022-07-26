from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Subscription, User
from .serializers import (
    SubscribeAddSerializer,
    SubscriptionSerializer,
    UserSerializerList,
)

ERROR_SUBSCRIBE = 'Такая подписка уже существует!'
ERROR_UNSUBSCRIBE = 'Такой подписки не существует!'


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    pagination_class = PageNumberPagination


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        current_user = self.request.user
        return Subscription.objects.filter(subscriber=current_user)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeAddSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        current_user = self.request.user
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        exists_subscribe = Subscription.objects.filter(
            author=user, subscriber=current_user
        ).exists()
        if exists_subscribe:
            return Response(
                {'errors': ERROR_SUBSCRIBE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = {'author': user.pk, 'subscriber': current_user.pk}
        serializer = SubscribeAddSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=False)
    def delete(self, request, *args, **kwargs):
        current_user = self.request.user
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        exists_subscribe = Subscription.objects.filter(
            author=user, subscriber=current_user
        ).exists()
        if not exists_subscribe:
            return Response(
                {'errors': ERROR_UNSUBSCRIBE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.filter(
            author=user, subscriber=current_user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
