from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from users.serializers import CustomUserSerializer

from foodgram.models import (Favorite, Ingredient, Purchase, Recipe,
                               RecipeIngredient, Subscription, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'ing_recipes')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = RecipeIngredientListSerializer(
        source='ing_in_recipe',
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    image = Base64ImageField(max_length=None, use_url=False,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        source='ing_in_recipe',
        many=True,
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(max_length=None, use_url=False,)

    class Meta:
        model = Recipe
        fields = (
            'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time'
        )

    def validate_tags(self, tags):
        if len(tags) > len(set(tags)):
            raise serializers.ValidationError(
                'Повторяющихся тегов в одном рецепе быть не должно!'
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Не выбраны ингредиенты!')
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredient_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredient_list.append(ingredient_id)
        return ingredients

    def _add_ingredients(self, recipe, ingredients):
        temp_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            temp_list.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_id,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(temp_list)

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ing_in_recipe')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ing_in_recipe')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self._add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    subscribed_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('user', 'is_subscribed')

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribed_to')
            )
        ]

    def validate_subscribed_to(self, is_subscribed):
        user = self.context['request'].user
        if user == is_subscribed:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return is_subscribed


class FavoritesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = Purchase
        fields = ('user', 'recipe')
