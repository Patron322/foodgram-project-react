from rest_framework.pagination import PageNumberPagination


class UserListPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class RecipeListPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'
