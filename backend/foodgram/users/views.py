from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status, permissions, viewsets, mixins
# from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .models import Follow
from api.pagination import CustomPageNumberPagination
from api.serializers import (FollowSerializer, FollowCreateDeleteSerializer,
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
@permission_classes([permissions.AllowAny])
def download_shopping_cart(request):
    user = request.user
    txt_file_output = shopping_cart_file(user)
    response = HttpResponse(txt_file_output, 'Content-Type: text/plain')
    response['Content-Disposition'] = (
        'attachment;' 'filename="Список_покупок.txt"'
    )
    return response


class UsersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_user(self):
        return self.request.user

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ('subscriptions', 'subscribe'):
            queryset = queryset.filter(
                following__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return queryset

    def get_permissions(self):
        if self.action in ('create', 'list', 'reset_password', ):
            self.permission_classes = (permissions.AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscriptions':
            return FollowSerializer
        elif self.action == 'subscribe':
            return FollowCreateDeleteSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        DjoserUserViewSet.perform_create(self, serializer)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        return DjoserUserViewSet.set_password(self, request, *args, **kwargs)

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
        # user, author = (serializer.validated_data.values())
        queryset = self.get_queryset().get(id=pk)
        instance_serializer = FollowSerializer(queryset, context=context)
        return Response(instance_serializer.data)
