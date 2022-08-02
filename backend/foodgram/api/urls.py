from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet,
    # UsersViewSet, signup_user, user_token,
)


router_v1 = DefaultRouter()
# router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    # path('v1/auth/signup/', signup_user, name='signup_user'),
    # path('v1/auth/token/', user_token, name='token'),
]
