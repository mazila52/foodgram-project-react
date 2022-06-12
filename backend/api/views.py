from rest_framework import generics
from foodgram.models import Recipe, Tag
from .serilalizers import RecipePostSerializer, TagSerializer
from rest_framework import filters, status, viewsets


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipePostSerializer





