import base64
from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (
    Ingredient, Tag, Recipe, ShoppingCart, IngredientInRecipe, Favorite
)
from users.serializers import UserSerializer

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "ingredient", "recipe", "amount")


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if ShoppingCart.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                {
                    'errors': 'рецепт уже в корзине'
                }
            )
        return {"user": User.objects.get(pk=user),
                "recipe": Recipe.objects.get(pk=recipe)}

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    # image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(
        source="recipe_ingredients",
        many=True
    )
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

    def get_is_favorited(self, obj):
        user = self.get.user()
        return (
            user.is_authenticated and
            user.favorites.filter(recipe=obj).exists
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.get.user()
        request = self.context.get('request')
        return (
            user.is_authenticated and
            ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'В рецепте отсутствуют ингредиенты!')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('В рецепте отсутствуют теги!')
        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Добавьте картинку рецепта!')
        return image

    def validate_name(self, name):
        if not name:
            raise serializers.ValidationError('Не заполнено название рецепта!')
        if self.context.get('request').method == 'POST':
            current_user = self.context.get('request').user
            if Recipe.objects.filter(author=current_user, name=name).exists():
                raise serializers.ValidationError(
                    'Рецепт с таким названием у вас уже есть!'
                )
        return name

    def validate_text(self, text):
        if not text:
            raise serializers.ValidationError('Не заполнено описание рецепта!')
        return text

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise serializers.ValidationError(
                'Не заполнено время приготовления рецепта!')
        return cooking_time


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                {
                    "errors": "Рецепт уже в избранном"
                }
            )

        return {
            "user": User.objects.get(pk=data['user']['id']),
            "recipe": Recipe.objects.get(pk=data['recipe']['id'])
        }

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        print(user, recipe)
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
