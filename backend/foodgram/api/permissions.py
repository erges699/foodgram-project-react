from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrOwnerOrReadOnly(BasePermission):
    message = 'Доступ разрешен только автору.'

    def has_permissions(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff


class SubscriberOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            obj == request.user or request.user.is_staff)
