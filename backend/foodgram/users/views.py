from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import (action, api_view,
                                       permission_classes, status)
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from .models import Follow
from api.pagination import CustomPageNumberPagination
from api.serializers import (ShowFollowsSerializer, FollowSerializer,
                             UserSerializer, UserCreateSerializer)
from recipes.models import IngredientsInRecipe

User = get_user_model()


def shopping_cart_file(user):
    ingredients = IngredientsInRecipe.objects.filter(
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
@permission_classes([permissions.IsAuthenticated])
def download_shopping_cart(request):
    user = request.user
    txt_file_output = shopping_cart_file(user)
    response = HttpResponse(txt_file_output, 'Content-Type: text/plain')
    response['Content-Disposition'] = (
        'attachment;' 'filename="Список_покупок.txt"'
    )
    return response


class UsersViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        return super(UsersViewSet, self).me(request, *args, **kwargs)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShowFollowsSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
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
    pagination_class = CustomPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
