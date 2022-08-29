from django.conf import settings
from django.contrib import admin

from .models import Ingredient, Recipe, Tag, IngredientsInRecipe
from users.models import ShoppingCart, Favorite


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_display_links = ('name',)
    search_fields = ('name', 'color', 'slug',)
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    search_help_text = 'Поиск по названию'
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]


class IngredientsInRecipeInline(admin.StackedInline):
    model = IngredientsInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'get_tags',
        'author',
        'get_ingredients',
        'name',
        'image',
        'text',
        'cooking_time',
    )
    filter_horizontal = ('tags',)
    inlines = (
        IngredientsInRecipeInline,
    )
    list_display_links = ('name',)
    search_fields = ('name', 'author', 'tags')
    search_help_text = 'Поиск по названию, автору и тегам'
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return "\n".join([tag.name for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return "\n".join([ingr.name for ingr in obj.ingredients.all()])


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = ('user', 'get_recipes')
    list_filter = ('user', 'recipes')
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        return '\n'.join([recipe.name for recipe in obj.recipes.all()])


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    filter_horizontal = ('recipes',)
    list_display = (
        'pk',
        'user',
        'get_recipes',
    )
    list_display_links = ('user',)
    list_filter = ('user', 'recipes')
    search_fields = ('user',)
    empty_value_display = settings.ADMIN_PAN_EMPTY_VALUE
    save_on_top = True
    actions = ['Delete', ]
    actions_on_top = True

    @admin.display(description='Рецепты')
    def get_recipes(self, obj):
        return '\n'.join([recipe.name for recipe in obj.recipes.all()])
