from django.contrib import admin

from .models import AmountRecipe, Favorite, Ingredient, Purchase, Recipe, Tag


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes')


class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'text',
        'show_ingredients',
        'show_tags',
        'cooking_time',
    )
    search_fields = ('name', 'author')

    def show_ingredients(self, obj):
        return "\n".join([a.name for a in obj.ingredients.all()])

    def show_tags(self, obj):
        return "\n".join([a.name for a in obj.tags.all()])


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


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Purchase, PurchaseAdmin)
admin.site.register(AmountRecipe, AmountRecipeAdmin)
