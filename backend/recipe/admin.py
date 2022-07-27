from django.contrib import admin

from .models import (Favorites, Follow, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'text',)
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')
    fields = ('name',
              'author',
              'text',
              'image',
              'cooking_time',
              'add_to_favorites',)
    readonly_fields = ('add_to_favorites',)
    empty_value_display = '-пусто-'

    def add_to_favorites(self, obj):
        return Favorites.objects.filter(recipe=obj).count()

    add_to_favorites.short_description = "Добавлен в избранное, раз"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe_id', 'amount', 'ingredient')
    search_fields = ('ingredient__name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)
    empty_value_display = '-пусто-'


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'tag', 'recipe')
    search_fields = ('tag',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user',)
    empty_value_display = '-пусто-'
