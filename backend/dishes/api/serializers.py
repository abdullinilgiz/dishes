import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShopItem, Tag)

User = get_user_model()


class DjoserUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', )

    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user.pk
        return Follow.objects.filter(
            follower=request_user, following=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientAmount
        fields = ('amount', 'name', 'id', 'measurement_unit', )

    def get_id(self, obj):
        return obj.ingredient.pk

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    author = DjoserUserSerializer()
    ingredients = IngredientAmountSerializer(many=True)
    image = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'image', 'text',
                  'cooking_time', 'is_favorited', 'is_in_shopping_cart',
                  'ingredients', )

    def get_is_favorited(self, obj):
        request_user = self.context['request'].user.pk
        return Favorite.objects.filter(
            user=request_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context['request'].user.pk
        return ShopItem.objects.filter(
            user=request_user, recipe=obj).exists()


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.pk')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount', )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientAmountCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'name', 'image', 'text', 'cooking_time', 'author',
                  'ingredients', )

    def validate(self, data):
        tags = data['tags']
        ingredients = data['ingredients']
        if not isinstance(tags, list) or len(tags) < 1:
            raise serializers.ValidationError('tags is a list with tag ids')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('tags should be unique')
        unique_ids = set()
        for ing in ingredients:
            if ing['amount'] < 1:
                raise serializers.ValidationError(
                    'amount is a positive integer')
            unique_ids.add(ing['ingredient']['pk'])
        if len(ingredients) != len(unique_ids):
            raise serializers.ValidationError('Ingredients should be unique')
        return data

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance,
                                      context={
                                          'request': self.context['request']})
        return serializer.data

    def create_ingredients(self, recipe, ingredients):
        ingredients_for_bulk_create = []
        for ing in ingredients:
            ingredient = get_object_or_404(
                Ingredient, pk=ing['ingredient']['pk'])
            ingredients_for_bulk_create.append(
                IngredientAmount(
                    ingredient=ingredient,
                    recipe=recipe,
                    amount=ing['amount'],
                )
            )
        IngredientAmount.objects.bulk_create(ingredients_for_bulk_create)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.all().delete()
        super().update(instance=instance, validated_data=validated_data)
        self.create_ingredients(instance, ingredients)
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class UserWithShortRecipesSerializer(DjoserUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', )

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            limit = max(1, int(limit))
            recipes = obj.recipes.all()[:limit]
        result = ShortRecipeSerializer(recipes, many=True)
        return result.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=False,
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe', )
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(
            instance.recipe, context={'request': self.context['request']})
        return serializer.data


class ShopItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        required=False,
    )

    class Meta:
        model = ShopItem
        fields = ('user', 'recipe', )
        validators = [
            UniqueTogetherValidator(
                queryset=ShopItem.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(
            instance.recipe, context={'request': self.context['request']})
        return serializer.data


class FollowSerialzier(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    following = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Follow
        fields = ('follower', 'following', )

    def validate(self, data):
        follower_id = data.get('follower')
        following_id = data.get('following')
        if follower_id == following_id:
            raise serializers.ValidationError(
                'It is impossible to follow youself.')
        if Follow.objects.filter(follower=follower_id,
                                 following=following_id).exists():
            raise serializers.ValidationError('Such follow already exist.')
        return data

    def to_representation(self, instance):
        serializer = UserWithShortRecipesSerializer(
            instance.following, context={'request': self.context['request']})
        return serializer.data
