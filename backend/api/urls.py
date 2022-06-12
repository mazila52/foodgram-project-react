from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagList, TagDetail, RecipeViewSet


router = DefaultRouter()
router.register(r'recipes',RecipeViewSet, basename='recipes')
urlpatterns = [
    path('', include('djoser.urls')),
    #path('', include('router.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('tags/', TagList.as_view()), 
    path('tags/<int:pk>/', TagDetail.as_view()),
    path('recipes/', include(router.urls)),    
]