from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializerList

from .models import (
    AmountRecipe,
    Favorite,
    Ingredient,
    Purchase,
    Recipe,
    RecipeTag,
    Tag,
)

ERROR_AMOUNT_VALUE = 'Количество ингредиента должно быть больше нуля!'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.pk',
    )
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserSerializerList()
    ingredients = IngredientInRecipeSerializer(
        many=True, source='amount_recipes'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user.pk
        return Favorite.objects.filter(
            user=current_user, recipes=obj.pk
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user.pk
        return Purchase.objects.filter(
            user=current_user, recipes=obj.pk
        ).exists()


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = AmountRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(ERROR_AMOUNT_VALUE)
        return value


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializerList(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(
        many=True, source='amount_recipes'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user.pk
        return Favorite.objects.filter(
            user=current_user, recipes=obj.pk
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user.pk
        return Purchase.objects.filter(
            user=current_user, recipes=obj.pk
        ).exists()

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount_recipes')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        ingredients = self.context['request'].data['ingredients']
        for ingredient in ingredients:
            ingredient_temp = Ingredient.objects.get(pk=ingredient['id'])
            AmountRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_temp,
                amount=ingredient['amount'],
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amount_recipes')
        ingredients = self.context['request'].data['ingredients']
        AmountRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            ingredient_temp = Ingredient.objects.get(pk=ingredient['id'])
            AmountRecipe.objects.create(
                recipe=instance,
                ingredient=ingredient_temp,
                amount=ingredient['amount'],
            )
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
