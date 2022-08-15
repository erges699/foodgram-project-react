from django.contrib import admin

from .models import Recipe, Ingredient, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'author', 'image', 'text', 'cooking_time',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class Ingredient(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug'
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'
