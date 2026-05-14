# Python modules
from typing import Any

# Third-party modules
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet


class RolePermissionMixin:
    """Helper methods for role and authentication checks."""

    def is_authenticated_user(self, request: DRFRequest) -> bool:
        """Return True if the request user is authenticated."""
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False))

    def is_admin_user(self, request: DRFRequest) -> bool:
        """Return True if the request user is a superuser or has ADMIN role."""
        if not self.is_authenticated_user(request):
            return False
        user = request.user
        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "role", None) == "ADMIN"
        )

    def is_editor_user(self, request: DRFRequest) -> bool:
        """Return True if the request user has EDITOR role."""
        if not self.is_authenticated_user(request):
            return False
        return getattr(request.user, "role", None) == "EDITOR"

    def is_editor_or_admin_user(self, request: DRFRequest) -> bool:
        """Return True if the request user is an editor or admin."""
        return self.is_editor_user(request) or self.is_admin_user(request)

    def extract_owner_id(self, obj: Any, *owner_fields: str) -> Any:
        """Return the first non-None owner ID found on obj for the given field names."""
        if isinstance(obj, int):
            return obj
        for field_name in owner_fields:
            owner_id = getattr(obj, field_name, None)
            if owner_id is not None:
                return owner_id
        return None

    def check_permission_or_deny(self, request: DRFRequest) -> None:
        """Raise PermissionDenied if has_permission returns False."""
        from rest_framework.exceptions import PermissionDenied

        if not self.has_permission(request, None):
            
            raise PermissionDenied(self.message)

    def check_object_permission_or_deny(self, request: DRFRequest, obj: Any) -> None:
        """Raise PermissionDenied if has_object_permission returns False."""
        from rest_framework.exceptions import PermissionDenied

        if not self.has_object_permission(request, None, obj):
            raise PermissionDenied(self.message)


class IsEditorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow access only for editor or admin roles."""

    message = "Forbidden! Only editors or admins can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """Return whether the request passes class-level permission checks."""
        return self.is_editor_or_admin_user(request)


class IsAdminOnly(RolePermissionMixin, BasePermission):
    """Allow access only for admin role."""

    message = "Forbidden! Only admins can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """Return whether the request passes class-level permission checks."""
        return self.is_admin_user(request)


class IsAuthorOrEditorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow object action to author, editor, or admin."""

    message = "Forbidden! Only author, editor, or admin can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """Return whether the request passes class-level permission checks."""
        return self.is_authenticated_user(request)

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Any
    ) -> bool:
        """Return whether the request is allowed for this target object."""
        if not self.is_authenticated_user(request):
            return False
        if self.is_editor_or_admin_user(request):
            return True
        author_id = self.extract_owner_id(obj, "author_id")
        return author_id == getattr(request.user, "id", None)


class IsCommentAuthorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow comment deletion/update for comment author or admin."""

    message = "Forbidden! Only comment author or admin can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """Return whether the request passes class-level permission checks."""
        return self.is_authenticated_user(request)

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Any
    ) -> bool:
        """Return whether the request is allowed for this target object."""
        if not self.is_authenticated_user(request):
            return False
        if self.is_admin_user(request):
            return True
        owner_id = self.extract_owner_id(obj, "user_id")
        return owner_id == getattr(request.user, "id", None)


class IsOwnerOrAdmin(RolePermissionMixin, BasePermission):
    """Allow action only for object owner or admin."""

    message = "Forbidden! You can modify only your own profile."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        """Return whether the request passes class-level permission checks."""
        return self.is_authenticated_user(request)

    def has_object_permission(
        self, request: DRFRequest, view: ViewSet, obj: Any
    ) -> bool:
        """Return whether the request is allowed for this target object."""
        if not self.is_authenticated_user(request):
            return False
        if self.is_admin_user(request):
            return True
        owner_id = self.extract_owner_id(obj, "id", "user_id")
        return owner_id == getattr(request.user, "id", None)
