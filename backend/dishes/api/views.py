from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.filters import FilterRecipe, SearchIngredientByName
from api.pagination import LimitPageNumberPagination
from api.permissions import CheckForOwnershipDELandPATCH
from api.serializers import (DjoserUserSerializer, FavoriteSerializer,
                             FollowSerialzier, IngredientSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             ShopItemSerializer, TagSerializer,
                             UserWithShortRecipesSerializer)
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShopItem, Tag)

User = get_user_model()


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet,):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get', ]
    permission_classes = (permissions.AllowAny, )


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet,):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get', ]
    permission_classes = [permissions.AllowAny, ]
    filter_backends = [SearchIngredientByName, ]


class DjoserUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = [permissions.AllowAny, ]
    pagination_class = LimitPageNumberPagination


@api_view(['GET', ])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def user_me(request):
    serializer = DjoserUserSerializer(request.user,
                                      context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          CheckForOwnershipDELandPATCH)
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    pagination_class = LimitPageNumberPagination
    filter_backends = [FilterRecipe, ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrive', ):
            return RecipeSerializer
        else:
            return RecipeCreateSerializer


class FollowListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet,):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['get', ]
    pagination_class = LimitPageNumberPagination
    serializer_class = UserWithShortRecipesSerializer

    def get_queryset(self):
        users_ids = Follow.objects.filter(
            follower=self.request.user).values('following')
        return User.objects.filter(id__in=users_ids)


class FollowCreateDestroyViewSet(mixins.CreateModelMixin,
                                 mixins.DestroyModelMixin,
                                 viewsets.GenericViewSet, ):
    queryset = Follow.objects.all()
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ['post', 'delete', ]
    serializer_class = FollowSerialzier

    def create(self, request, *args, **kwargs):
        get_object_or_404(User, pk=self.kwargs.get('user_id'))
        serializer = self.get_serializer(data={
            'follower': request.user.pk,
            'following': self.kwargs.get('user_id'),
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        following = get_object_or_404(User, pk=self.kwargs.get('user_id'))
        instance = self.queryset.filter(
            following=following,
            follower=self.request.user
        )
        if not instance.exists():
            raise ValidationError('Instance do not exist')
        return instance


@api_view(['GET', ])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def download_shopping_cart(request):
    ingredients = IngredientAmount.objects.filter(
        recipe__in=Recipe.objects.filter(
            id__in=ShopItem.objects.filter(
                user=request.user).values('recipe')
        )
    ).prefetch_related('ingredient')
    name_amount = dict()
    name_unit = dict()
    for ing in ingredients:
        name = ing.ingredient.name
        if name in name_amount:
            name_amount[name] += ing.amount
        else:
            name_amount[name] = ing.amount
        name_unit[name] = ing.ingredient.measurement_unit
    result = str()
    for name, amount in name_amount.items():
        result += name + ': ' + str(amount) + ' ' + name_unit[name] + '\n'
    response = HttpResponse(
        result,
        content_type='text/plain; charset=UTF-8'
    )
    response['Content-Disposition'] = ('attachment; filename={0}'.format(
        'shoppinglist.txt'))
    return response


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'user': self.request.user.pk,
            'recipe': self.kwargs.get('recipe_id')
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        instance = self.queryset.filter(recipe=recipe, user=self.request.user)
        if not instance.exists():
            raise ValidationError('Instance do not exist')
        return instance


class ShopItemViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet,):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            'user': self.request.user.pk,
            'recipe': self.kwargs.get('recipe_id')
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
        instance = self.queryset.filter(recipe=recipe, user=self.request.user)
        if not instance.exists():
            raise ValidationError('Instance do not exist')
        return instance
