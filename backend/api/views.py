import csv

from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from foodgram.models import (Favorite, Ingredient, Purchase, Recipe,
                             RecipeIngredient, Subscription, Tag)
from users.models import User

from .filters import RecipeFilter
from .paginators import RecipesCustomPagination
from .permissions import OwnerOrReadOnly
from .serilalizers import (FavoritesSerializer, IngredientSerializer,
                           PurchaseSerializer,
                           RecipeListSerializer, RecipePostSerializer,
                           SubscriptionSerializer, TagSerializer)


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer
    permission_classes = [OwnerOrReadOnly, ]
    filter_backends = (DjangoFilterBackend, RecipeFilter)
    filterset_fileds = ('tags__slug',)
    ordering = ('-id')
    pagination_class = RecipesCustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipePostSerializer

    @action(detail=True, methods=['post', ])
    def favorite(self, request, pk):
        user = User.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=pk)
        data = {
            'recipe': recipe.id,
        }
        serializer = FavoritesSerializer(data=data)
        serializer.is_valid()
        serializer.save(user=user)
        return Response(status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        user = User.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=pk)
        instance = Favorite.objects.get(user=user, recipe=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', ])
    def shopping_cart(self, request, pk):
        user = User.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=pk)
        data = {
            'recipe': recipe.id,
        }
        serializer = PurchaseSerializer(data=data)
        serializer.is_valid()
        serializer.save(user=user)
        return Response(status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        user = User.objects.get(id=request.user.id)
        recipe = Recipe.objects.get(id=pk)
        instance = Purchase.objects.get(user=user, recipe=recipe)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', ])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__purchase__user=request.user
            ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            ingredient_amount=Sum('amount')
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_amount'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shoppinglist.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for row in list(ingredients):
            writer.writerow(row)
        return response

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Recipe.objects.all()
        is_in_shopping = self.request.query_params.get('is_in_shoppong_cart')
        is_favorite = self.request.query_params.get('is_favorite')
        is_favor = Favorite.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user
        )
        in_cart = Purchase.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user
        )
        queryset = Recipe.objects.annotate(
            is_favor=Exists(is_favor)
            ).annotate(is_cart=Exists(in_cart))
        if is_favorite == '1':
            return queryset.filter(is_favor=True)
        if is_in_shopping == '1':
            return queryset.filter(in_cart=True)
        return Recipe.objects.all()


class SubscriptionList(generics.ListAPIView):
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user__id=self.request.user.id)


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    ordering_fileds = ('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_fileds = ('name',)
