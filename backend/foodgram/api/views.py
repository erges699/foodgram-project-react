<<<<<<< HEAD
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken

from .filters import IngredientFilter, RecipeFilter
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
    # filterset_class = IngredientFilter

    # def get_queryset(self):
    #    name = self.request.GET.get('name')
    #    if name:
    #        return Ingredient.objects.filter(name__istartswith=name)
    #    return Ingredient.objects.all()


'''
    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=self.kwargs.get('review_id'),
                title_id=self.kwargs.get('title_id')
            )
        )
'''


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (permissions.AllowAny,)
=======
from django.db.models import Aggregate, Count, Sum, Exists, OuterRef, Subquery
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
    IngredientsInRecipe, ShoppingCartSerializer
)
from .utils import create_pdf
from recipes.models import Ingredient, Tag, Recipe
from users.models import Favorite, ShoppingCart


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
>>>>>>> 20220817_v41_api_ser_0822-0923
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
<<<<<<< HEAD
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
=======
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset
        queryset = self.queryset.annotate(
            is_favorited=Exists(
                user.favorite.filter(recipes=OuterRef('pk'))),
            is_in_shopping_cart=Exists(
                user.shoppingcart_set.filter(recipes=OuterRef('pk'))),
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
            filter(recipes__author=user).
            values('ingredients__id').
            order_by('ingredients__id')
        )

        shopping_list = (
            ingredient_list_user.annotate(amount=Sum('amount')).
            values_list(
                'ingredients__name', 'ingredients__measurement_unit', 'amount'
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
>>>>>>> 20220817_v41_api_ser_0822-0923
