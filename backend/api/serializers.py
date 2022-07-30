from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField

from recipes.models import (
    AmountRecipe,
    Favorite,
    Ingredient,
    Purchase,
    Recipe,
    RecipeTag,
    Tag,
)
from users.models import Subscription, User

ERROR_AMOUNT_VALUE = 'Количество ингредиента должно быть больше нуля!'
ERROR_COOKING_TIME = 'Время приготовления должно быть больше нуля!'
ERROR_COUNT_TAGS = 'Невозможно создать рецепт без тегов!'
ERROR_COUNT_INGREDIENTS = 'Невозможно создать рецепт без ингредиентов!'
ERROR_UNIQUE_TAGS = 'Теги в рецепте должны быть уникальными!'
ERROR_UNIQUE_INGREDIENTS = 'Ингредиенты в рецепте должны быть уникальными!'
ERROR_AMOUNT = 'Количество ингредиента должно быть больше 1!'


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


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    id = serializers.IntegerField(source='author.pk')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user.pk
        return Subscription.objects.filter(
            author=obj.author, subscriber=current_user
        ).exists()

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class SubscribeAddSerializer(serializers.ModelSerializer):
    subscriber = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionSerializer(instance, context=context).data


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

    def validate(self, attrs):
        if attrs['cooking_time'] < 1:
            raise serializers.ValidationError(ERROR_COOKING_TIME)
        if len(attrs['tags']) == 0:
            raise serializers.ValidationError(ERROR_COUNT_TAGS)
        if len(attrs['amount_recipes']) == 0:
            raise serializers.ValidationError(ERROR_COUNT_INGREDIENTS)
        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise serializers.ValidationError(ERROR_UNIQUE_TAGS)
        ingredients = []
        for ingredient in attrs['amount_recipes']:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(ERROR_AMOUNT)
            ingredients.append(ingredient['id'])
        if len(ingredients) > len(set(ingredients)):
            raise serializers.ValidationError(ERROR_UNIQUE_INGREDIENTS)
        return attrs

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

    def add_ingredients(self, recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_temp = Ingredient.objects.get(pk=ingredient['id'])
            ingredients_list.append(
                AmountRecipe(
                    recipe=recipe,
                    ingredient=ingredient_temp,
                    amount=ingredient['amount'],
                )
            )
        return AmountRecipe.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('amount_recipes')
        recipe = Recipe.objects.create(author=author, **validated_data)
        tag_list = []
        for tag in tags:
            tag_list.append(RecipeTag(recipe=recipe, tag=tag))
        RecipeTag.objects.bulk_create(tag_list)
        ingredients = self.context['request'].data['ingredients']
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('amount_recipes')
        ingredients = self.context['request'].data['ingredients']
        AmountRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(instance, ingredients)
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
