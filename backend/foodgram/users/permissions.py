from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """
    Права доступа: только чтение.
    read: any
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdmin(permissions.BasePermission):
    """
    Права доступа: Администратор.
    read: admin
    write: admin

    Superuser is always an admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminModeratorOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Права доступа: Администратор, Модератор, Автор или только чтение.
    read: any
    post: authenticated
    patch|delete: author, moderator, admin
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
