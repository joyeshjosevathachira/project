from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read access (GET/HEAD/OPTIONS) to anyone.
    Allow write access (POST/PUT/PATCH/DELETE) only to staff/admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
