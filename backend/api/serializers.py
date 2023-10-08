import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from recipes.models import (Ingredient, Recipe, RecipeIngredient, ShoppingCart,
                            Tag)
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='photo.' + ext)

        return super().to_internal_value(data)


class UsersCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password')

        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с таким именем!'
            )
        return value


class UsersSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=object.id).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True)
    author = UsersSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def validate(self, data):
        list_ingr = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, distinct_ingredients = (
            len(list_ingr), len(set(list_ingr)))

        if all_ingredients != distinct_ingredients:
            raise ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        return data

    def get_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UsersSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:

        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UsersSerializer):
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(UsersSerializer.Meta):
        fields = UsersSerializer.Meta.fields + ('recipes', 'recipes_count')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, object):
        from api.serializers import RecipeInfoSerializer

        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return RecipeInfoSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()
