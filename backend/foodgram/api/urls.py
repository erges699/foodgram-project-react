from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet, TagViewSet, FavouriteViewSet,
    IngredientViewSet, ShoppingCartViewSet,
)
from users.views import UsersViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(
        'recipes/(?P<id>[^/.]+)/favorite',
        FavouriteViewSet,
        basename='favorite'
)
router_v1.register(
    'recipes/(?P<id>[^/.]+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shoppinglist'
)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
