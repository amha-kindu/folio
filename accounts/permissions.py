from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with the admin role.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "admin")


class IsAdminOrStaffRole(permissions.BasePermission):
    """
    Allows access to users with admin or staff role.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in {"admin", "staff"}
        )
