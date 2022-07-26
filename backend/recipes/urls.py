from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    DownloadShoppingCart,
    FavoriteViewSet,
    IngredientViewSet,
    RecipesViewSet,
    ShoppingCartViewSet,
    TagViewSet,
)

app_name = 'recipes'

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite_recipe',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart',
)
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('', include(router.urls)),
]
