from django.contrib import admin
from django.contrib.auth import get_user_model
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShopItem, Tag)

User = get_user_model()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', )


class IngredientAmountInline(admin.StackedInline):
    model = IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorite_count', )
    list_filter = ('name', 'author', 'tags', )
    readonly_fields = ('favorite_count', )

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj.id).count()
    favorite_count.short_description = 'Favorite count'

    inlines = [
        IngredientAmountInline,
    ]


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe', )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )


class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', )


class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', )


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', )
    list_filter = ('username', 'email',)

    empty_value_display = '-empty-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShopItem, ShopItemAdmin)
admin.site.register(User, UserAdmin)
