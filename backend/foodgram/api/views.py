from rest_framework import (filters, permissions, status, viewsets,)

from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer, RecipeCreateUpdateSerializer,
    RecipeFollowSerializer, ShoppingCartSerializer 
)
from recipes.models import Ingredient, Tag, Recipe
from users.models import ShoppingCart


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (permissions.AllowAny, )
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    # permission_classes = (permissions.AllowAny,)


class ShoppingCartView(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    # permission_classes = (permissions.AllowAny, )