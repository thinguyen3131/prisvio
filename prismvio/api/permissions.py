from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """
    This permission allows a user with 'is_staff' (is_admin) permission to make all changes (CREATE, UPDATE, DELETE).
     Users other than 'is_staff' (is_admin) only have permission to view the object (READ).
    """

    def has_permission(self, request, view):
        # Allow SAFE_METHODS (GET, HEAD, OPTIONS) methods for all users
        if request.method in SAFE_METHODS:
            return True

        # Check if user has 'is_staff' (is_admin) permission
        return request.user.is_staff


class IsBusinessAdminOrAdmin(BasePermission):
    """
    This permission allows users with 'business_admin' or 'is_staff'
    (is_admin) permission to make all changes (CREATE, UPDATE, DELETE).
     Users other than 'business_admin' or 'is_staff' (is_admin) only
     have permission to view the object (READ).
    """

    def has_permission(self, request, view):
        # Allow SAFE_METHODS (GET, HEAD, OPTIONS) methods for all users
        if request.method in SAFE_METHODS:
            return True

        # Check if user has 'business admin' or 'is_staff' (is_admin) permission
        return request.user.business_admin or request.user.is_staff


class CanDeleteMerchant(BasePermission):
    def has_permission(self, request, view):
        # Cho phép is_superuser có quyền delete
        if request.method == "DELETE" and request.user.is_superuser:
            return True
        return False
