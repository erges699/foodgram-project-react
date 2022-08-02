# from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX',
        unique=True,
    )
    slug = models.CharField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'



class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Ссылка на картинку на сайте'
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов',
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        # validators=(
        #     MinValueValidator(1, 'Время приготовления от 1 ')
        # ),
    )

    class Meta:
        ordering = ('-pk', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'

    def get_absolute_url(self):
        return reverse('recipe', args=[self.pk])


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )    
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'amount',),
                name='unique_amount_of_ingredient',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name}: {self.amount}'
            f'{self.ingredient.measurement_unit}'
        )
