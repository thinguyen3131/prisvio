from django.contrib.auth import get_user_model
from rest_framework import permissions

from prismvio.merchant.models import Merchant
from prismvio.staff.models import Staff

User = get_user_model()


# An account must be logged in to be used except to retrieve data
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
        if isinstance(obj, Merchant) and obj.owner == request.user:
            return True
        if isinstance(obj, Staff) and obj.user == request.user:
            return True

        return False


# These are the supper admin and admin accounts
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
        if isinstance(obj, Merchant) and obj.owner == request.user:
            return True
        if isinstance(obj, Staff) and obj.user == request.user:
            return True

        return False


class IsGetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check for the user role for GET method or user role for other methods
        if request.method == "GET":
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Allow any permission for GET requests or the user role for other methods
        if request.method == "GET":
            return True

        # Check for ownership.
        is_authenticated = bool(request.user and request.user.is_authenticated)
        if is_authenticated and isinstance(obj, User) and obj == request.user:
            return True
        return False


# This is a Merchant account that must be logged in
class MerchantPermission(permissions.BasePermission):
    """
    Custom permission for Merchant model.
    """

    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        if is_authenticated and isinstance(obj, Merchant) and obj.owner == request.user:
            return True
        return False
