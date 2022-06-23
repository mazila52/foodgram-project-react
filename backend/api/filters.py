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
