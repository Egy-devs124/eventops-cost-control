from rest_framework.permissions import BasePermission


def user_role_code(user):
    if not user or not user.is_authenticated:
        return None
    role = getattr(user, "role", None)
    return getattr(role, "code", None)


class RoleScopedPermission(BasePermission):
    """Simple role guard used by viewsets.

    Viewsets can set `allowed_roles` for all actions and/or
    `role_permissions = {"action": ["role"]}` for action-specific rules.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        action = getattr(view, "action", None)
        role_permissions = getattr(view, "role_permissions", {})
        allowed = role_permissions.get(action) or getattr(view, "allowed_roles", None)
        if not allowed:
            return True
        return user_role_code(request.user) in allowed

    def has_object_permission(self, request, view, obj):
        object_filter = getattr(view, "can_access_object", None)
        if callable(object_filter):
            return object_filter(request.user, obj)
        return self.has_permission(request, view)
