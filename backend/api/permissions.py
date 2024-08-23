from rest_framework.permissions import (BasePermission, IsAuthenticated,
                                        SAFE_METHODS)


class IsUserViewPermitted(BasePermission):
    def has_permission(self, request, view):
        return (
            request.path != '/api/users/me/'
            or request.user.is_authenticated
        )


class IsAdminOrOwnerOrReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user or request.user.is_superuser
        )
