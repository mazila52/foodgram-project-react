import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from foodgram.models import (Favorite, Ingredient, Purchase, Recipe,
                             RecipeIngredient, Subscription, Tag)
from .filters import RecipeFilter
from .paginators import RecipesCustomPagination
from .permissions import OwnerOrReadOnly
from .serilalizers import (FavoritesSerializer, IngredientSerializer,
                           PurchaseSerializer, RecipeListSerializer,
                           RecipePostSerializer, SubscriptionSerializer,
                           TagSerializer)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = [AllowAny, ]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


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

    def _add_favorite_or_purchase(self, request, pk, input_serializer):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'recipe': recipe.id,
        }
        serializer = input_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

    def _del_favorite_or_purchase(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        instance = get_object_or_404(model, user=user, recipe=recipe)
        instance.delete()

    @action(detail=True, methods=['post', ])
    def favorite(self, request, pk):
        self._add_favorite_or_purchase(request, pk, FavoritesSerializer)
        return Response(status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        self._del_favorite_or_purchase(request, pk, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', ])
    def shopping_cart(self, request, pk):
        self._add_favorite_or_purchase(request, pk, PurchaseSerializer)
        return Response(status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        self._del_favorite_or_purchase(request, pk, Purchase)
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
