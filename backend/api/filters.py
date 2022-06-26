from django.db.models import Exists, OuterRef
from foodgram.models import Favorite, Purchase
from rest_framework.filters import BaseFilterBackend


class RecipeFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = request.user
        if user.is_anonymous:
            return queryset
        
        is_in_shopping = request.query_params.get('is_in_shoppong_cart')
        is_favorite = request.query_params.get('is_favorite')
        is_favor = Favorite.objects.filter(
            recipe=OuterRef('pk'),
            user=user
        )
        in_cart = Purchase.objects.filter(
            recipe=OuterRef('pk'),
            user=user
        )
        queryset = queryset.annotate(
            is_favor=Exists(is_favor)
            ).annotate(is_cart=Exists(in_cart))
        if is_favorite == '1':
            queryset = queryset.filter(is_favor=True)
        if is_in_shopping == '1':
            queryset = queryset.filter(in_cart=True)
        return queryset
