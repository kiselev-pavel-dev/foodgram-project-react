from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Favorite, Purchase, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name='author__id', lookup_expr='exact')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        favorites = Favorite.objects.filter(user=self.request.user).all()
        return queryset.filter(
            pk__in=(favorite.recipes.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        recipes = Purchase.objects.filter(user=self.request.user).all()
        return queryset.filter(
            pk__in=(recipe.recipes.pk for recipe in recipes)
        )
