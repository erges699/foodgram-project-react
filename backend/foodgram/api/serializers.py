from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredient, Tag, Recipe, IngredientsInRecipe, User
)
from users.models import (
    Follow, ShoppingCart, Favorite
)


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through
    post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """
    def to_internal_value(self, data):
        import base64
        import six
        import uuid
        from django.core.files.base import ContentFile

        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4())[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


class UserCreateSerializer(UserCreateSerializer):
    """Done"""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )


class UserSerializer(UserSerializer):
    """Done"""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name',
        )


class TagSerializer(serializers.ModelSerializer):
    """Done"""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'author')


class IngredientSerializer(serializers.ModelSerializer):
    """Done"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeReadSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='name')
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient_name', 'measurement_unit', 'amount')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredient')
    tags = TagSerializer(many=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        """
        Функция проверки добавления рецепта в избранное.
        """

        if self.context.get('request').method == 'POST':
            return False

        if self.context.get('request').user.is_authenticated:
            return obj.is_favorited
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Функция проверки добавления рецепта рецепта в список покупок.
        """

        if self.context.get('request').method == 'POST':
            return False

        if self.context.get('request').user.is_authenticated:
            return obj.is_in_shopping_cart
        return False


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        source='recipe_ingredient')
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    image = Base64ImageField(max_length=None, use_url=True,)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def ingredients_tags_add(self, instance, ingrs_data):
        IngredientsInRecipe.objects.bulk_create(
                [
                    IngredientsInRecipe(
                        ingredient_id=ingredient['ingredient']['id'],
                        amount=ingredient['amount'],
                        recipe=instance
                    )
                    for ingredient in ingrs_data
                ]
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        # tags_data = validated_data.pop('tags')
        # for ingr in ingredients_data:
        #     instance.ingredients.add(ingr['id'].id, ingr['amount'])
        # for tag in tags_data:
        #     instance.tags.add(tag)
        instance = super().create(validated_data)
        return self.ingredients_tags_add(instance, ingredients_data)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = self.ingredients_tags_add(
            instance, ingredients_data, tags_data
            )
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': instance.recipe.image.url,
            'cooking_time': instance.recipe.cooking_time,
        }
        print(instance)
        print(data)
        return data

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class FollowerSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'recipes',
        )


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        model = Follow
        fields = ('user', 'author',)
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Такая подписка уже существует!'
            )
        ]

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя!'
            )
        return data


class ShowFollowsSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe',)


class RecipeFollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
