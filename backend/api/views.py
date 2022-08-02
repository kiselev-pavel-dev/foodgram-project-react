from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Purchase, Recipe, Tag
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    SubscribeAddSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserSerializerList,
)
from .utils import download_shopping_cart

ERROR_ADD_TO_FAVORITE = 'Рецепт уже есть в избранном!'
ERROR_DELETE_FROM_FAVORITE = 'Нет такого рецепта в избранном!'
ERROR_ADD_TO_CART = 'Рецепт уже есть в списке покупок!'
ERROR_DELETE_FROM_CART = 'Нет такого рецепта в списке покупок!'
ERROR_SUBSCRIBE = 'Такая подписка уже существует!'
ERROR_UNSUBSCRIBE = 'Такой подписки не существует!'


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializerList
    queryset = User.objects.all()
    pagination_class = PageNumberPagination


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = None
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


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter]
    pagination_class = None
    search_fields = ('^name',)


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return RecipeWriteSerializer
        return RecipeSerializer


class FavoriteViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        exists_favorite = Favorite.objects.filter(
            user=user, recipes=recipe
        ).exists()
        if exists_favorite:
            return Response(
                {'errors': ERROR_ADD_TO_FAVORITE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.create(user=user, recipes=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=False)
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        exists_favorite = Favorite.objects.filter(
            user=user, recipes=recipe
        ).exists()
        if not exists_favorite:
            return Response(
                {'errors': ERROR_DELETE_FROM_FAVORITE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.filter(user=user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Purchase.objects.all()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        exists_shopping_cart = Purchase.objects.filter(
            user=user, recipes=recipe
        ).exists()
        if exists_shopping_cart:
            return Response(
                {'errors': ERROR_ADD_TO_CART},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Purchase.objects.create(user=user, recipes=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['DELETE'], detail=False)
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        exists_shopping_cart = Purchase.objects.filter(
            user=user, recipes=recipe
        ).exists()
        if not exists_shopping_cart:
            return Response(
                {'errors': ERROR_DELETE_FROM_CART},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Purchase.objects.filter(user=user, recipes=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        return download_shopping_cart(request)
