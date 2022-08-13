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

from .paginators import SmallPageNumberPagination
from recipes.models import Follow, IngredientInRecipe
from api.serializers import (FollowSerializer, ShowFollowsSerializer,
                             UserSerializer, FollowerSerializer)

User = get_user_model()


def shopping_cart_file(user):
    ingredients = IngredientInRecipe.objects.filter(
        recipe__buying__user=user).values(
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
    pagination_class = SmallPageNumberPagination

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        return super(UsersViewSet, self).me(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FollowerSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id=None):
        serializer = FollowSerializer(
            data=dict(author=id, user=request.user.id),
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            user=request.user,
            author=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'Попытка удалить несуществующую подписку!'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowViewSet(ListAPIView):
    serializer_class = ShowFollowsSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = SmallPageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
