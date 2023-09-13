from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (DjoserUserViewSet, FavoriteViewSet,
                       FollowCreateDestroyViewSet, FollowListViewSet,
                       IngredientViewSet, RecipeViewSet, ShopItemViewSet,
                       TagViewSet, download_shopping_cart, user_me)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users/subscriptions',
                FollowListViewSet, basename='follow-get')
router.register('users', DjoserUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/', user_me, name='download-shop-items'),
    path('recipes/download_shopping_cart/',
         download_shopping_cart, name='download-shop-items'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShopItemViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopitem-create-destroy'),
    path('users/<int:user_id>/subscribe/',
         FollowCreateDestroyViewSet.as_view({'post': 'create',
                                             'delete': 'destroy'}),
         name='follow-post-delete'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
         name='shopitem-create-destroy'),
    path('', include(router.urls)),
]
