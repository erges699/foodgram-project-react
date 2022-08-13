from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions, status, viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken

from .filters import RecipeFilter
# from .permissions import IsAdmin, IsAdminModeratorOwnerOrReadOnly, ReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeFollowSerializer, ShoppingCartSerializer,
    # SignUpSerializer, TokenSerializer, UserSerializer,
)
from recipes.models import Ingredient, Tag, Recipe
# from users.models import User


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
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter

    def get_queryset(self):
        is_favorited = self.request.GET.get("is_favorited")
        is_in_shopping_cart = self.request.GET.get("is_in_shopping_cart")
        if is_favorited:
            return Recipe.objects.filter(favourite__user=self.request.user)
        if is_in_shopping_cart:
            return Recipe.objects.filter(buying__user=self.request.user)
        return Recipe.objects.all().order_by('-id')


class ShoppingCartView(viewsets.ModelViewSet):
    # permission_classes = (permissions.AllowAny, )

    @action(methods=['get', 'delete'], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def get(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe, user=request.user)
        serializer = RecipeFollowSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        shopping_cart = get_object_or_404(
            ShoppingCartSerializer,
            user=user,
            recipe__id=recipe_id
        )
        shopping_cart.delete()
        return Response(
            f'Рецепт {shopping_cart.recipe} '
            f'удален из корзины пользователя {user}, '
            f'status=status.HTTP_204_NO_CONTENT'
        )
