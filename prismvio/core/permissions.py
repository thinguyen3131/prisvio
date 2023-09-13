from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import BasePermission

User = get_user_model()


class IsBusinessAdminOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admin to edit/delete and allow anyone to read.
    """

    def has_permission(self, request, view):
        # Allow any permission for GET requests
        if request.method == "GET":
            return True

        # Check for the user role for other methods
        if request.user.role in ["Admin", "SuperAdmin"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Allow any permission for GET requests
        if request.method == "GET":
            return True

        # Check for the user role for other methods
        if request.user.role in ["Admin", "SuperAdmin"]:
            return True

        # Check for ownership for User, Merchant, Staff
        if isinstance(obj, User) and obj == request.user:
            return True
        # if isinstance(obj, Merchant) and obj.owner == request.user:
        #     return True
        # if isinstance(obj, Staff) and obj.user == request.user:
        #     return True

        return False


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow specific roles to perform actions.
    """

    def has_permission(self, request, view):
        # Check for the user role for GET method
        if request.method == "GET":
            if request.user.role in ["Admin", "SuperAdmin"]:
                return True
            return False

        # Check for the user role for other methods
        if request.user.role in ["Admin", "SuperAdmin"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Check for the user role for GET method
        if request.method == "GET":
            if request.user.role in ["Admin", "SuperAdmin"]:
                return True
            return False

        # Check for the user role for other methods
        if request.user.role in ["Admin", "SuperAdmin"]:
            return True

        # Check for ownership for User, Merchant, Staff
        if isinstance(obj, User) and obj == request.user:
            return True
        # if isinstance(obj, Merchant) and obj.owner == request.user:
        #     return True
        # if isinstance(obj, Staff) and obj.user == request.user:
        #     return True

        return False


class CanDeleteMerchant(BasePermission):
    def has_permission(self, request, view):
        # Cho phép is_superuser có quyền delete
        if request.method == "DELETE" and request.user.is_superuser:
            return True
        return False


class IsGetPermission(BasePermission):
    def has_permission(self, request, view):
        # Check for the user role for GET method or user role for other methods
        if request.method == "GET":
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Allow any permission for GET requests or the user role for other methods
        if request.method == "GET":
            return True

        # Check for ownership for User, Merchant, Staff
        if isinstance(obj, User) and obj == request.user:
            return True
        return False
