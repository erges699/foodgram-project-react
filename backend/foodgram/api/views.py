from django.db.models import Exists, OuterRef, Sum
from django.http import FileResponse
from rest_framework import (filters, viewsets, status, permissions, mixins)
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .filters import RecipeFilter
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateUpdateSerializer, IngredientsInRecipe,
    FavoriteShoppingSerializer
)
from .services import create_pdf
from recipes.models import Ingredient, Tag, Recipe


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = (permissions.AllowAny,)
        elif self.action in ('update', 'destroy', 'partial_update'):
            permission_classes = (IsOwnerOrReadOnly,)
        else:
            permission_classes = (permissions.IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            favorite = user.favorite_recipes.filter(id=OuterRef('id'))
            shopping_list = user.shopping_recipes.filter(id=OuterRef('id'))
            return Recipe.objects.annotate(
                is_favorited=Exists(favorite),
                is_in_shopping_cart=Exists(shopping_list)
            )
        return Recipe.objects.all()

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


class FavoriteAndShoppingCartDady(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
    mixins.DestroyModelMixin,
):
    permission_classes = (permissions.IsAuthenticated,)
    model_class = Recipe
    error = 'Указанный рецепт не был добавлен в список покупок.'


class FavouriteViewSet(FavoriteAndShoppingCartDady):
    def get_queryset(self):
        user = self.request.user
        return user.favorite_recipes

    def get_serializer(self, id):
        return FavoriteShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'favorite',
            },
            context={
                'request': self.request,
            }
        )


class ShoppingCartViewSet(FavoriteAndShoppingCartDady):
    def get_queryset(self):
        user = self.request.user
        return user.shopping_recipes

    def get_serializer(self, id):
        return FavoriteShoppingSerializer(
            data={
                'recipe': id,
                'user': self.request.user.id,
                'type_list': 'shopping',
            },
            context={
                'request': self.request,
            }
        )
