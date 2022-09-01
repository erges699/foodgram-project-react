from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientsFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrOwnerOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer, IngredientsInRecipe,
    RecipeCreateUpdateSerializer, RecipeSerializer, ShoppingCartSerializer,
    TagSerializer,
)
from .services import create_pdf
from recipes.models import Ingredient, Recipe, Tag
from users.models import Favorite, ShoppingCart


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = None
    filter_backends = (IngredientsFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (
        IsAdminOrOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset
        return self.queryset.annotate(
            is_favorited=Exists(
                user.favorite_set.filter(recipes=OuterRef('pk'))),
            is_in_shopping_cart=Exists(
                user.shoppingcart_set.filter(recipes=OuterRef('pk'))),
        )

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return ShoppingCartSerializer
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
            filter(recipe__author=user).
            values('ingredient__id').
            order_by('ingredient__id')
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

    def favorite_shopping_cart(self, user_model, request, pk):
        serializer = self.get_serializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        instance, _ = user_model.objects.get_or_create(user=self.request.user)
        if request.method == 'DELETE':
            instance.recipes.remove(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        instance.recipes.add(pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self.favorite_shopping_cart(
            Favorite,
            request,
            pk
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self.favorite_shopping_cart(
            ShoppingCart,
            request,
            pk
        )
