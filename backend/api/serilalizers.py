from dataclasses import field, fields
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from foodgram.models import Ingredient, Recipe, RecipeIngredient, Tag, Subscription, User
from rest_framework.validators import UniqueTogetherValidator
from drf_extra_fields.fields import Base64ImageField
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient')
    class Meta:
        model = RecipeIngredient
        fields = ('id','amount')

    
class RecipePostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(many=True, required=False)
    tags = serializers.PrimaryKeyRelatedField(
        many = True,
        read_only = True
    )
    image = Base64ImageField(max_length=None, use_url=False,)
    
    class Meta:
        model = Recipe
        fields = ('author','ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.get('tags')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients:
            id=ingredient['ingredient']
            ingredient_id = Ingredient.objects.get(id=id)
            amount = ingredient['amount']
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient_id, amount=amount)
        
        return recipe

class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        #default=serializers.CurrentUserDefault()
    )
    is_subscribed = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('user', 'is_subscribed')

        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'is_subscribed')
            )
        ]

    def validate_is_subscribed(self, is_subscribed):
        user = self.context['request'].user
        if user == is_subscribed:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return is_subscribed