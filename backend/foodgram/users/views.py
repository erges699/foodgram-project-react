from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from api.pagination import CustomPageNumberPagination
from api.permissions import SubscriberOrAdmin
from api.serializers import (
    FollowCreateDeleteSerializer, FollowSerializer, UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
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
                recipes_count=Count('recipes'),
            )
        return queryset

    def get_permissions(self):
        if self.action in ('create', 'list', 'reset_password', ):
            self.permission_classes = (permissions.AllowAny,)
        elif self.action == 'subscribe':
            self.permission_classes = (
                SubscriberOrAdmin,
                permissions.IsAuthenticatedOrReadOnly
            )
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

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        return super().set_password(self, request, *args, **kwargs)

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
    def subscribe(self, request, id=None):
        context = {'request': request}
        data = {
            'user': self.get_user().id,
            'author': (id)
        }
        serializer = self.get_serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        if request.method == 'DELETE':
            instance = get_object_or_404(Follow, **serializer.initial_data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        queryset = self.get_queryset().get(id=id)
        instance_serializer = FollowSerializer(queryset, context=context)
        return Response(instance_serializer.data, status.HTTP_201_CREATED)
