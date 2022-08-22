from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from rest_framework import (filters, permissions, status, viewsets,)
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from .filters import RecipeFilter
from .pagination import CustomPageNumberPagination
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateUpdateSerializer, FavoriteSerializer,
    IngredientsInRecipe, ShowFollowsSerializer
)
from .utils import create_pdf
from recipes.models import Ingredient, Tag, Recipe
from users.models import Favorite, Follow, ShoppingCart

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset
        queryset = self.queryset.annotate(
            is_favorited=Exists(
                user.favorite_set.filter(recipes=OuterRef('pk'))),
            is_in_shopping_cart=Exists(
                user.cart_set.filter(recipes=OuterRef('pk'))),
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False,
            methods=['GET', ], url_path='download_shopping_cart',)
    def download_shopping_cart(self, request):
        user = request.user
        ingredient_list_user = (
            IngredientsInRecipe.objects.
            prefetch_related('ingredients', 'recipes').
            filter(recipe__shoppings=user).
            values('ingredients__id').
            order_by('ingredients__id')
        )

        shopping_list = (
            ingredient_list_user.annotate(amount=Sum('amount')).
            values_list(
                'ingredient__name', 'ingredient__measurement_unit', 'amount'
            )
        )

        file = create_pdf(shopping_list, 'Список покупок')

        return FileResponse(
            file,
            as_attachment=True,
            filename='shopping_list.pdf',
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        instance, _ = Favorite.objects.get_or_create(user=self.request.user)

        if request.method == 'DELETE':
            if not instance.recipes.filter(pk=pk).exists():
                message = {'errors': 'Такого рецепта нет в избранном'}
                raise ValidationError(message)
            instance.recipes.remove(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if instance.recipes.filter(pk=pk).exists():
            message = {'errors': 'Такой рецепт уже есть в избранном'}
            raise ValidationError(message)
        instance.recipes.add(pk)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        serializer = ShoppingCart(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        instance, _ = ShoppingCart.objects.get_or_create(user=self.request.user)

        if request.method == 'DELETE':
            if not instance.recipes.filter(pk=pk).exists():
                message = {'errors': 'Такого рецепта нет в списке покупок'}
                raise ValidationError(message)
            instance.recipes.remove(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if instance.recipes.filter(pk=pk).exists():
            message = {'errors': 'Такой рецепт уже есть в списке покупок'}
            raise ValidationError(message)
        instance.recipes.add(pk)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
