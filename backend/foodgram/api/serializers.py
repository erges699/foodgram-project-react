from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'tag',
            'cooking_time'
        )
