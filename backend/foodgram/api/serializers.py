from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe
from users.models import User
from users.validators import username_validator


class UsernameValidationMixin():

    def validate_username(self, value):
        username_validator(value)
        return value


class SignUpSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )


class TokenSerializer(UsernameValidationMixin, serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(UsernameValidationMixin, serializers.ModelSerializer):

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = User


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'measurement_unit', 'amount')
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
