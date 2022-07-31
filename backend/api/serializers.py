from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorites, Follow, Ingredient, Recipe,
                           RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import User


def for_ingredient(self, ingredients):
    for ingredient in ingredients:
        ingredient_obj = get_object_or_404(Ingredient,
                                           id=ingredient['id'])
        RecipeIngredient.objects.create(
            recipe_id=self,
            ingredient=ingredient_obj,
            amount=ingredient['amount']
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class MetaUserSerializers:
    model = User
    fields = ('email',
              'id',
              'username',
              'first_name',
              'last_name',
              'password',)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(MetaUserSerializers):
        pass


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name=None)

    class Meta(MetaUserSerializers):
        pass

    def get_is_subscribed(self, obj):
        if self.context['request'].auth is None:
            return False
        user = self.context['request'].user
        author = get_object_or_404(User, pk=obj.id)
        return Follow.objects.filter(user=user, author=author).exists()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name=None)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.user.is_anonymous:
            return False
        user = self.context['request'].user
        author = get_object_or_404(User, pk=obj.id)
        return Follow.objects.filter(user=user, author=author).exists()


class RecipeIngredientsSerializer(serializers.HyperlinkedModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(source='recipeingredient_set',
                                              read_only=True,
                                              many=True)
    is_favorited = serializers.SerializerMethodField(method_name=None)
    is_in_shopping_cart = serializers.SerializerMethodField(method_name=None)

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        read_only_fields = ('is_favorite', 'is_shopping_cart')

    def get_is_favorited(self, obj):
        if self.user.is_anonymous:
            return False
        user = self.context['request'].user
        return Favorites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.user.is_anonymous:
            return False
        user = self.context['request'].user
        if ShoppingCart.objects.filter(user=user, recipe=obj).exists():
            return True
        return False

    def validate(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) < 1:
            raise serializers.ValidationError()

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым')
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient,
                                               id=ingredient['id'])
            if ingredient_obj in ingredient_list:
                raise serializers.ValidationError(
                    'Нельзя добавить один и тот же ингридиент несколько раз')
            ingredient_list.append(ingredient_obj)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0')
        data['ingredients'] = ingredients

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Список тэгов не может быть пустым'})
        tag_list = []
        for tag in tags:
            tag_obj = get_object_or_404(Tag, id=int(tag))
            if tag_obj in tag_list:
                raise serializers.ValidationError(
                    'Нельзя добавить один и тот же тэг несколько раз')
            tag_list.append(tag_obj)
        data['tags'] = tags

        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)

        recipe.tags.set(tags)
        for_ingredient(self, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        instance.tags.clear()
        tags = self.validated_data.get('tags', instance.tags)
        instance.tags.set(tags)

        RecipeIngredient.objects.filter(recipe_id=instance).all().delete()
        ingredients = validated_data.get('ingredients', instance.ingredients)
        for_ingredient(self, ingredients)

        instance.save()
        return instance

    def for_ingredient(self, ingredients):
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient,
                                               id=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe_id=self,
                ingredient=ingredient_obj,
                amount=ingredient['amount']
            )

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddFavoritesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddFollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name=None)
    recipes_count = serializers.SerializerMethodField(method_name=None)
    recipes = serializers.SerializerMethodField(method_name=None)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return AddFavoritesSerializer(queryset, many=True).data

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user,
                                     author=obj.author).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.select_related(author=obj.author).count()
