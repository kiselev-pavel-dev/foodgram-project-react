from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .models import Favorite, Ingredient, Purchase, Recipe, Tag
from .permissions import AuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)
from .utils import download_shopping_cart

ERROR_ADD_TO_FAVORITE = 'Рецепт уже есть в избранном!'
ERROR_DELETE_FROM_FAVORITE = 'Нет такого рецепта в избранном!'
ERROR_ADD_TO_CART = 'Рецепт уже есть в списке покупок!'
ERROR_DELETE_FROM_CART = 'Нет такого рецепта в списке покупок!'


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
