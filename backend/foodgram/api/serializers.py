from rest_framework import serializers

from recipes.models import (
    Ingredient, Tag, Recipe, ShoppingCart, IngredientInRecipe
) 
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientInRecipeSerizlizer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerizlizer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'tag',
            'cooking_time'
        )

    def get_user(self):
        return self.context['request'].user

    def get_is_favorited(self,obj):
        
        user = self.get.user()
        return (
            user.is_authenticated and
            user.favorites.filter(recipe=obj).exists
        )
