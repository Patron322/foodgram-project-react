from unicodedata import name
from attr import field, fields
from django.db import models
from django.db.models import F, Q
from sqlalchemy import UniqueConstraint
from users.models import User


class Tag(models.Model):
    """Тэги рецептов."""

    name = models.CharField(
        'Тэг',
        max_length=200,
        unique=True,
        help_text='Тэг')
    color = models.CharField(
        'Цвет тэга',
        max_length=7,
        blank=True,
        unique=True,
        help_text='Цветовой HEX-код')
    slug = models.SlugField(
        'Префикс',
        max_length=200,
        blank=True,
        unique=True,
        help_text='Префикс')

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ингридиенты"""

    name = models.CharField(
        'Название ингридиента',
        max_length=200,
        help_text='Название ингридиента')
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
        help_text='Единица измерения ингридиента')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingridient')
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепты"""

    name = models.CharField(
        'Название рецепта',
        max_length=200,
        help_text='Название рецепта')
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор рецепта'
    )
    text = models.TextField(
        'Описание рецепта',
        help_text='Описание рецепта'
    )
    image = models.ImageField(
        'Картинка рецепта',
        upload_to='media/',
        max_length=None,
        null=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги рецепта',
        through='RecipeTag'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        help_text='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        'Дата и время написания рецепта',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """Модель рецепта и тэга"""

    tag = models.ForeignKey(
        Tag,
        verbose_name='Тэг',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'


class RecipeIngredient(models.Model):
    """Ингредиенты блюда"""

    recipe_id = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        on_delete=models.CASCADE,
        help_text='Ингредиент блюда'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Название продукта',
        on_delete=models.CASCADE,
        help_text='Название продукта'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        help_text='Количество ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Favorites(models.Model):
    """Избранные рецепты."""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
        help_text='Имя подписчика'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favourites',
        help_text='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_favorite'),
        )


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='cart_user',
        help_text='Имя пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='cart_recipe',
        help_text='Рецепт в списке покупок'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique_shopping_cart'),
        )


class Follow(models.Model):
    """Система подписок"""

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Имя подписчика'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='following',
        help_text='Имя автора рецепта'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_follow'),
            models.CheckConstraint(check=~Q(user=F('author')),
                                   name='subscribe_to_yourself'),
        )
