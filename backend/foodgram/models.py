from pyexpat import model
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model


class Tag(models.Model):
    name = models.CharField(
        max_length=200
    )
    color = models.CharField(
        max_length=7
    )
    slug = models.SlugField(
        max_length=200
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
    
    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Рецепты автора',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    tags = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipe_img/'
    )
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField('Время приготовления')

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.SmallIntegerField('Количество')


class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    is_subscribed = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='is_subscribed')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_subscribed'],
                name='user_not_subscribe_himself'
            )
        ]
