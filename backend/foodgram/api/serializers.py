from djoser.serializers import UserCreateSerializer as UserCreate
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientsInRecipe, Recipe, Tag, User
from users.models import Favorite, Follow, ShoppingCart


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return user.follower.filter(author=obj).exists()


class UserCreateSerializer(UserCreate):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):

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
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
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
        source='ingredient_recipe')
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)
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


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
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
        source='ingredient_recipe')
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

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

        set_tag_id = set()
        for tag in value:
            tag_id = tag.id
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Такого тега не существует!'
                )
            if tag_id in set_tag_id:
                raise serializers.ValidationError(
                    "В рецепте не может быть нескольких одинаковых тегов!"
                )
            set_tag_id.add(tag_id)
        return value

    def validate_ingredients(self, value):
        if len(value) == 0:
            raise serializers.ValidationError(
                'Укажите ингредиенты для рецепта.'
            )
        set_ingr_id = set()
        for ingredient in value:
            ingredient_id = ingredient['ingredient']['id']
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f"Ингредиент с id {ingredient_id} нам не завезли!"
                )
            if ingredient_id in set_ingr_id:
                raise serializers.ValidationError(
                    "В рецепте не может быть нескольких одинаковых "
                    "ингредиентов. Проверьте - ингредиент с "
                    f"id {ingredient_id}"
                )
            set_ingr_id.add(ingredient_id)
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    "Количество ингредиента должно быть более 0!"
                    f"Добавьте ещё ингредиента с id {ingredient_id}."
                )
        return value

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
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredient_recipe')
        instance = super().create(validated_data)
        return self.ingredients_tags_add(instance, ingredients_data)

    def update(self, instance, validated_data):
        instance.tags.set(validated_data.get('tags', instance.tags))
        ingredients_data = validated_data.pop('ingredient_recipe')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.ingredients_tags_add(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return result


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )

    def to_representation(self, instance):
        serializer = RecipeMinifiedSerializer(
            instance.get('recipes'),
        )
        return serializer.data

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipes')


class FavoriteSerializer(serializers.ModelSerializer):
    recipes = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    def to_representation(self, instance):
        serializer = RecipeMinifiedSerializer(
            instance.get('recipes'),
        )
        return serializer.data

    class Meta:
        model = Favorite
        fields = ('user', 'recipes')


class FollowSerializer(UserSerializer):
    recipes_count = serializers.IntegerField()
    recipes = serializers.SerializerMethodField()

    def validate(self, data):
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                if recipes_limit < 0:
                    raise ValueError
            except ValueError:
                message = 'Параметр recipes_limit должен быть числом больше 0'
                raise serializers.ValidationError(message)

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        serializer = RecipeMinifiedSerializer(
            obj.recipes.all()[:recipes_limit],
            many=True,
        )
        return serializer.data

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


class FollowCreateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')
