from django.contrib import admin

from .models import (
    AmountRecipe,
    Favorite,
    Ingredient,
    Purchase,
    Recipe,
    RecipeTag,
    Tag,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes')


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes')


class RecipeAdmin(admin.ModelAdmin):
    fields = (
        'author',
        'name',
        'text',
        'show_ingredients',
        'show_tags',
        'cooking_time',
        'count_favorite',
    )
    list_display = (
        'pk',
        'author',
        'name',
        'text',
        'show_ingredients',
        'show_tags',
        'cooking_time',
        'count_favorite',
    )

    def show_ingredients(self, obj):
        return "\n".join([a.name for a in obj.ingredients.all()])

    def show_tags(self, obj):
        return "\n".join([a.name for a in obj.tags.all()])

    def count_favorite(self, obj):
        return Favorite.objects.filter(recipes=obj).count()

    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ['show_ingredients', 'show_tags', 'count_favorite']
    count_favorite.short_description = 'Количество добавления в избранное'
    show_ingredients.short_description = 'Ингредиенты'
    show_tags.short_description = 'Теги'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)


class AmountRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount',
    )


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'tag')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(AmountRecipe, AmountRecipeAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
