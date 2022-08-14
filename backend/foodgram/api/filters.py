from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    FilterSet
)

from recipes.models import Recipe, ShoppingCart

# def get_queryset(self):
#     is_favorited = self.request.GET.get("is_favorited")
#     is_in_shopping_cart = self.request.GET.get("is_in_shopping_cart")
#     if is_favorited:
#         return Recipe.objects.filter(favourited__user=self.request.user)
#     if is_in_shopping_cart:
#         return Recipe.objects.filter(buying__user=self.request.user)
#     return Recipe.objects.all().order_by('-id')


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        favorites = self.request.user.favorites.all()
        return queryset.filter(
            pk__in=(favorite.recipe.pk for favorite in favorites)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        try:
            recipes = (
                self.request.user.shopping_cart.recipes.all()
            )
        except ShoppingCart.DoesNotExist:
            return queryset
        return queryset.filter(
            pk__in=(recipe.pk for recipe in recipes)
        )
