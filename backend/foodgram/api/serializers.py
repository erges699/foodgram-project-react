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
    ingredients = IngredientInRecipeSerializer(source="recipe_ingredients", many=True)
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
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Basket.objects.filter(user=request.user, recipe=obj).exists()

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'В рецепте не заполнены ингредиенты!')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError('В рецепте не заполнены теги!')
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

    def create_recipe_ingredients(self, ingredients, recipe):
        for i in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=i.get('id'),
                amount=i.get('amount'),
            )

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str),
                           name='{}.{}'.format(name, ext))

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        self.create_recipe_ingredients(
            self.validate_ingredients(self.initial_data.get('ingredients', instance.ingredients)), instance)
        instance.name = validated_data.get('name', instance.name)
        img = validated_data.get('image')
        if not img:
            img = instance.image
        else:
            img = self.base64_file(img)
        instance.image = img
        instance.text = validated_data.get('text', instance.text)
        instance.tags.set(self.validate_tags(self.initial_data.get('tags', instance.tags)))
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        current_user = self.context.get('request').user
        ingredients = self.validate_ingredients(
            self.initial_data.get('ingredients')
        )
        name = self.validate_name(
            self.initial_data.get('name')
        )
        image = self.base64_file(self.validate_image(
            self.initial_data.get('image')
        ))
        text = self.validate_text(
            self.initial_data.get('text')
        )
        tags = self.validate_tags(
            self.initial_data.get('tags')
        )
        cooking_time = self.validate_cooking_time(
            self.initial_data.get('cooking_time')
        )
        recipe = Recipe.objects.create(
            author=current_user,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time
        )
        self.create_recipe_ingredients(
            ingredients,
            recipe
        )
        recipe.tags.set(tags)
        return recipe


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
