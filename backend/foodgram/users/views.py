from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .models import Follow
from api.pagination import CustomPageNumberPagination
from api.serializers import (FollowSerializer, ShowFollowsSerializer,
                             UserSerializer, UserCreateSerializer, FollowerSerializer)
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
@permission_classes([permissions.AllowAny])
def download_shopping_cart(request):
    user = request.user
    txt_file_output = shopping_cart_file(user)
    response = HttpResponse(txt_file_output, 'Content-Type: text/plain')
    response['Content-Disposition'] = (
        'attachment;' 'filename="Список_покупок.txt"'
    )
    return response


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (permissions.IsAuthenticated,)    
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return UserCreateSerializer
        return UserSerializer

    def get_user(self):
        return self.request.user
        
    def get_permissions(self):
        if self.action in ('create', 'list', 'reset_password', ):
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ('subscriptions', 'subscribe'):
            queryset = queryset.filter(
                following__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return queryset

    def me(self, request):
        """
        Метод для обработки запроса GET на получение данных профиля текущего
        пользователя.
        URL - /users/me/.
        """

        user = request.user
        serializer = self.get_serializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )        
    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        context = {'request': request}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, pk=None):
        context = {'request': request}
        data = {
            'user': self.get_user().pk,
            'author': (pk,),
        }
        serializer = self.get_serializer(data=data)
        if request.method == 'DELETE':
            instance = get_object_or_404(Follow, **serializer.initial_data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        queryset = self.get_queryset().get(id=pk)
        instance_serializer = FollowSerializer(queryset, context=context)
        return Response(instance_serializer.data)
