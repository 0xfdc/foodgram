from rest_framework.permissions import BasePermission


class IsUserViewPermitted(BasePermission):
    def has_permission(self, request, view):
        return (
            request.path != '/api/users/me/'
            or request.user.is_authenticated
        )
