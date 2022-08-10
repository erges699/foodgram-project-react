import django_filters
from recipes.models import Recipe, Ingredient


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
