from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

CHOICES = (
    ('#FFFFFF', 'Белый'),
    ('#000000', 'Чёрный'),
    ('#0000FF', 'Синий'),
    ('#00FF00', 'Лайм'),
    ('#FF0000', 'Красный'),
    ('#FFFF00', 'Жёлтый'),
    ('#FFC0CB', 'Розовый'),
    ('#D2691E', 'Шоколадный'),
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=7,
        default='#FFFFFF',
        verbose_name='Цвет в HEX',
        choices=CHOICES,
        help_text='Введите цвет тега',
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Слаг тега',
        help_text='Введите уникальный слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[self.slug])


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
        help_text='Введите единицу измерения',
        )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('-name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
        help_text='Выбирите теги',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredients',
        through='IngredientsInRecipe',
        verbose_name='Список ингредиентов',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Ссылка на картинку на сайте',
        help_text='Изображение рецепта',
    )
    text = models.TextField(
        verbose_name='Описание',
        default='',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Список тегов',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1)],
        help_text='Введите текст рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(
            1,
            message='Минимальное время приготовления 1 минута')
        ],
        default=1,
    )

    class Meta:
        ordering = ('-pk', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'

    def get_absolute_url(self):
        return reverse('recipe', args=[self.pk])

    def get_number_add_to_favourite(self):
        return self.favorites.count()

    def get_number_ingredients(self):
        return self.ingredients.count()


class IngredientsInRecipe(models.Model):
    recipes = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipe_ingredient',
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='recipe_ingredient',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)],
        default=1
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipes', 'ingredients',),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredients}: {self.amount}'
        )
