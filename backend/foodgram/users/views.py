from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from .paginators import SmallPageNumberPagination

from .models import Follow
from recipes.models import IngredientInRecipe
from api.serializers import (FollowSerializer, ShowFollowsSerializer,
                             UserSerializer, FollowerSerializer)

User = get_user_model()


def shopping_cart_file(user):
    ingredients = IngredientInRecipe.objects.filter(
        recipe__in_shopping_cart__user=user).values(
        'ingredient__name',
        'ingredient__unit').annotate(total=Sum('amount'))

    shopping_list = 'список:\n'
    for number, ingredient in enumerate(ingredients, start=1):
        shopping_list += (
            f'{number} '
            f'{ingredient["ingredient__name"]} - '
            f'{ingredient["total"]} '
            f'{ingredient["ingredient__unit"]}\n')
    return shopping_list


@api_view(['GET', ])
# @permission_classes([permissions.IsAuthenticated])
def download_shopping_cart(request):
    user = request.user
    txt_file_output = shopping_cart_file(user)
    response = HttpResponse(txt_file_output, 'Content-Type: text/plain')
    response['Content-Disposition'] = (
        'attachment;' 'filename="Список_покупок.txt"'
    )
    return response


class UsersViewSet(UserViewSet):
    serializer_class = UserSerializer


class FollowViewSet(ListAPIView):
    serializer_class = ShowFollowsSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
