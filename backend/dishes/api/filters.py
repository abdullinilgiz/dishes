from rest_framework import filters

from recipes.models import Favorite, ShopItem


class SearchIngredientByName(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name = request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__startswith=name)
        return queryset


class FilterRecipe(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        is_favorited = request.query_params.get('is_favorited')
        is_shoplist = request.query_params.get('is_in_shopping_cart')
        author_id = request.query_params.get('author')
        tags = request.query_params.getlist('tags')
        if is_favorited:
            queryset = queryset.filter(
                id__in=Favorite.objects.filter(
                    user=request.user).values('recipe'))
        if is_shoplist:
            queryset = queryset.filter(
                id__in=ShopItem.objects.filter(
                    user=request.user).values('recipe'))
        if author_id:
            queryset = queryset.filter(
                author=author_id)
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags
            ).distinct()
        return queryset
