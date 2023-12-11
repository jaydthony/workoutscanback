from rest_framework import permissions

class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow superusers to edit, while others can only view.
    """

    def has_permission(self, request, view):
        # Allow read-only access to anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write access only to superusers
        return request.user and request.user.is_superuser


class IsSuperuserOrReadOnlyExceptPOST(IsSuperuserOrReadOnly):
    def has_permission(self, request, view):
        # Allow POST requests without checking superuser status
        if request.method == 'POST':
            return True

        # Apply the original permission logic for other methods (GET, PATCH, DELETE)
        return super().has_permission(request, view)