from rest_framework import (filters, viewsets, status)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)

from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateUpdateSerializer, ShoppingCartSerializer,
    FavoriteSerializer
)
from recipes.models import Ingredient, Tag, Recipe
from users.models import ShoppingCart, Favorite


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
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
    serializer_class = RecipeSerializer
    # permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        data = {
            'user': self.request.user.pk,
            'recipe': pk,
        }
        if request.method == 'DELETE':
            instance = get_object_or_404(Favorite, **data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = FavoriteSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        serializer = ShoppingCartSerializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        instance, _ = ShoppingCart.objects.get_or_create(
            user=self.request.user
            )

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


class ShoppingCartView(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    # permission_classes = (permissions.AllowAny, )
