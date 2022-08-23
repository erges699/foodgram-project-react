from django.urls import include, path
from rest_framework.routers import DefaultRouter

<<<<<<< HEAD
from .views import (
    RecipeViewSet, TagViewSet, IngredientViewSet,
    # UsersViewSet, signup_user, user_token,
)


router_v1 = DefaultRouter()
# router_v1.register('users', UsersViewSet, basename='users')
=======
from .views import RecipeViewSet, TagViewSet, IngredientViewSet
from users.views import UsersViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
>>>>>>> 20220817_v41_api_ser_0822-0923
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls')),
<<<<<<< HEAD
    path('auth/', include('djoser.urls.jwt')),
    # path('v1/auth/signup/', signup_user, name='signup_user'),
    # path('v1/auth/token/', user_token, name='token'),
=======
    path('auth/', include('djoser.urls.authtoken')),
>>>>>>> 20220817_v41_api_ser_0822-0923
]
