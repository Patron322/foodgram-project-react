from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipe.models import (Favorites, Follow, Ingredient, Recipe,
                           ShoppingCart, Tag)
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import RecipeListPagination, UserListPagination
from .permissions import AuthorOrReadOnly
from .serializers import (AddFavoritesSerializer, AddFollowSerializer,
                          CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)
from .utils import download_shopping_cart


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для вывода списка тегов рецепта
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipeListPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = RecipeFilter

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            if Favorites.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Рецепт \"{recipe.name}\" '
                               'уже есть в избранном у пользователя '
                               f'{user.username}'},
                    status=HTTP_400_BAD_REQUEST
                )
            Favorites.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            obj = Favorites.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'У пользователя {user.username} '
                           f'в избранном нет рецепта \"{recipe.name}\"'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': f'Рецепт \"{recipe.name}\" '
                               'уже есть в списке покупок у пользователя '
                               f'{user.username}'},
                    status=HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = AddFavoritesSerializer(recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            obj = ShoppingCart.objects.filter(user=user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'У пользователя {user.username} '
                           f'в списке покупок нет рецепта \"{recipe.name}\"'},
                status=HTTP_400_BAD_REQUEST
            )

        download_shopping_cart(self, request)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = UserListPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        if request.method == 'POST':
            user = request.user
            author = get_object_or_404(User, id=pk)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': f'Пользователь \"{user.username}\" '
                               'уже подписан на '
                               f'{author.username}'},
                    status=HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(user=user, author=author)
            serializer = AddFollowSerializer(follow,
                                             context={'request': request})
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            user = request.user
            author = get_object_or_404(User, id=pk)
            obj = Follow.objects.filter(user=user, author__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Пользователь {user.username} '
                           f'не подписан на {author.username}\"'},
                status=HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='subscriptions', url_name='subscriptions',
            permission_classes=[permissions.IsAuthenticated],
            serializer_class=AddFollowSerializer)
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = AddFollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permissions_calsses = (permissions.IsAuthenticated,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
