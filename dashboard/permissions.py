from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only access is allowed for any request.
    """

    def has_permission(self, request, view):
        # Allow all GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the admin users.
        return request.user and request.user.is_staff
