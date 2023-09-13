from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.TextField(
        unique=True,
        max_length=200
    )
    color = models.CharField(
        unique=True,
        max_length=7
    )
    slug = models.SlugField(
        unique=True,
        max_length=30
    )

    def __str__(self) -> str:
        return str(self.slug)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
    )
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message='1 is minimal value')])
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        ordering = ['-pub_date']


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='only_unique_ingredients',
            )
        ]


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredient_amount',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message='1 is minimal value')]
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredients',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='only_unique_ingredient_recipe',
            )
        ]


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='only_unique_follows',
            )
        ]


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Favorite(UserRecipe):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='only_unique_favorites',
            )
        ]


class ShopItem(UserRecipe):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='only_unique_shopitems',
            )
        ]
