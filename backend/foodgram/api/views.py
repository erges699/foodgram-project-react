from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST
)

from .filters import CustomSearchFilter, RecipieFilter
from .pagination import CustomPageNumberPagination
from .fields import Base64ImageField
from .serializers import (
    IngredientSerializer, TagSerializer, RecipeSerializer,
    RecipeCreateUpdateSerializer, ShoppingCartSerializer,
    RecipeFollowSerializer,
)
from recipes.models import (
    Ingredient, Tag, Recipe, IngredientsInRecipe, User
)
from users.models import (Follow, ShoppingCart)


class UserCreateSerializer(UserCreateSerializer):
    """Done"""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class UserSerializer(UserSerializer):
    """Done"""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            # 'is_subscribed',
        )
        # read_only_fields = ('is_subscribed', )

        #validators = [
        #    UniqueTogetherValidator(
        #        queryset=User.objects.all(),
        #        fields=("username", "email"),
        #        message=(
        #            "Задано не уникальное сочетание полей email " "и username."
        #        ),
        #    ),
        #]

    # def get_is_subscribed(self, obj):
    #    if self.context.get('request').path_info == '/api/users/me/':
    #        return False
    #    user = self.context.get('request').user
    #    if user.is_authenticated:
    #        try:
    #            return obj.is_subscribed
    #        except AttributeError:
    #            return user.subscriber.filter(user_author=obj).exists()
    #    return False
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    def get_user(self):
        return self.request.user

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ('subscriptions', 'subscribe'):
            queryset = queryset.filter(
                following__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return queryset

        @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        context = {'request': request}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, pk=None):
        context = {'request': request}
        data = {
            'user': self.get_user().pk,
            'author': (pk,),
        }
        serializer = self.get_serializer(data=data)
        if request.method == 'DELETE':
            instance = get_object_or_404(Follow, **serializer.initial_data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # user, author = (serializer.validated_data.values())
        queryset = self.get_queryset().get(id=pk)
        instance_serializer = FollowSerializer(queryset, context=context)
        return Response(instance_serializer.data)


class TagSerializer(serializers.ModelSerializer):
    """Done"""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Done"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):
    """Done"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientsInRecipeReadSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='name')
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'ingredient_name',
            'measurement_unit',
            'amount'
        )


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
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredient')
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
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
            'is_favorited',
            'is_in_shopping_cart',
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
        fields = (
            'id',
            'amount'
        )


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

    def validate_tags(self, value):
        if len(value) == 0:
            raise serializers.ValidationError('Укажите теги рецепта')

        for tag in value:
            if tag not in Tag.objects.all():
                raise serializers.ValidationError(
                    'Такого тега не существует!'
                )
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Укажите ингредиенты для рецепта.'
            )
        set_ingr_id = set()
        for ingredient in value:
            ingredients_id = ingredient['ingredients']['id']
            if not Ingredient.objects.filter(id=ingredients_id).exists():
                raise serializers.ValidationError(
                    f"Ингредиент с id {ingredients_id} нам не завезли!"
                )
            if ingredients_id in set_ingr_id:
                raise serializers.ValidationError(
                    "В рецепте не может быть нескольких одинаковых "
                    "ингредиентов. Проверьте - ингредиент с "
                    f"id {ingredients_id}"
                )
            set_ingr_id.add(ingredients_id)
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть более 0!"
                    f"Добавьте ещё ингредиента с id {ingredients_id}."
                )
        return value

    def ingredients_tags_add(self, instance, ingrs_data):
        IngredientsInRecipe.objects.bulk_create(
                [
                    IngredientsInRecipe(
                        ingredients_id=ingredient['ingredients']['id'],
                        amount=ingredient['amount'],
                        recipes=instance
                    )
                    for ingredient in ingrs_data
                ]
            )
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredient')
        instance = super().create(validated_data)
        return self.ingredients_tags_add(instance, ingredients_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        instance.tags.set(validated_data.get('tags', instance.tags))
        instance.ingredients.clear()
        instance.save()

        self.ingredients_tags_add(
            instance, validated_data['recipe_ingredient']
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['tags'] = TagSerializer(instance.tags.all(), many=True).data

        return result


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    """Done"""

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    type_list = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'recipe',
            'user',
            'type_list',
        )

    def validate(self, data):
        recipe = get_object_or_404(Recipe, id=data['recipe'].id)

        if data['type_list'] == 'favorite':
            error_text = 'список избранного'
            condition = User.objects.select_related('favorite_recipes').filter(
                username=data['user'].username,
                favorite_recipes=recipe
            ).exists()
        if data['type_list'] == 'shopping':
            error_text = 'список покупок'
            condition = User.objects.select_related('shopping_recipes').filter(
                username=data['user'].username,
                shopping_recipes=recipe
            ).exists()

        if condition:
            raise serializers.ValidationError(
                    f"Рецепт {recipe} уже добавлен в {error_text}."
            )

        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']

        if validated_data['type_list'] == 'favorite':
            user.favorite_recipes.add(recipe)
        if validated_data['type_list'] == 'shopping':
            user.shopping_recipes.add(recipe)

        return recipe

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(instance).data


class ShowFollowsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.only('id', 'name', 'image', 'cooking_time')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = User
        fields = (
            'user',
            'user_author',
            'type_list'
        )

    def validate(self, data):
        user = data['user']
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        if Follow.objects.filter(user=user, user_author=author).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на пользователя {author}.'
            )
        return data

    def create(self, validated_data):
        user = validated_data['user']
        author = validated_data['author']
        Follow.objects.create(
            user=user,
            author=author
        )
        return user

    def to_representation(self, instance):
        data = instance.subscribing.annotate(
            is_subscribed=User.objects.all()).last().exists()

        return ShowFollowsSerializer(
            data,
            context={
                'request': self.context.get('request'),
            }
        ).data
