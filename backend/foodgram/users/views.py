from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import RefreshToken
# from .permissions import IsAdmin, IsAdminModeratorOwnerOrReadOnly, ReadOnly

from .serializers import (UserSerializer,)

from .models import User

class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    lookup_field = 'username'
    serializer_class = UserSerializer
    pagination_class = pagination.PageNumberPagination

    @action(methods=['get', 'PATCH'], detail=False,
            permission_classes=[permissions.IsAuthenticated],
            url_path='me', url_name='me')
    def personal_profile(self, request, *args, **kwargs):
        instance = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=instance.role)
        return Response(serializer.data)
