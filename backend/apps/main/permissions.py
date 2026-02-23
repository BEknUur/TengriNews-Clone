"""Project permission classes for TengriNews API."""

# Python modules
from typing import Any

# Django REST Framework modules
from rest_framework.permissions import BasePermission
from rest_framework.request import Request as DRFRequest
from rest_framework.viewsets import ViewSet


class RolePermissionMixin:
    """Helper methods for role and authentication checks."""

    def _is_authenticated(self, request: DRFRequest) -> bool:
        user = getattr(request, "user", None)
        return bool(user and getattr(user, "is_authenticated", False))

    def _is_admin(self, request: DRFRequest) -> bool:
        if not self._is_authenticated(request):
            return False

        user = request.user
        user_role = getattr(user, "role", None)

        return bool(
            getattr(user, "is_superuser", False)
            or user_role == "ADMIN"
        )

    def _is_editor(self, request: DRFRequest) -> bool:
        if not self._is_authenticated(request):
            return False

        return getattr(request.user, "role", None) == "EDITOR"

    def _is_editor_or_admin(self, request: DRFRequest) -> bool:
        return self._is_editor(request) or self._is_admin(request)

    def _extract_owner_id(self, obj: Any, *owner_fields: str) -> Any:
        if isinstance(obj, int):
            return obj

        for field_name in owner_fields:
            owner_id = getattr(obj, field_name, None)
            if owner_id is not None:
                return owner_id

        return None


class IsEditorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow access only for editor or admin roles."""

    message = "Forbidden! Only editors or admins can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        return self._is_editor_or_admin(request)


class IsAdminOnly(RolePermissionMixin, BasePermission):
    """Allow access only for admin role."""

    message = "Forbidden! Only admins can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        return self._is_admin(request)


class IsAuthorOrEditorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow object action to author, editor, or admin."""

    message = "Forbidden! Only author, editor, or admin can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        return self._is_authenticated(request)

    def has_object_permission(self, request: DRFRequest, view: ViewSet, obj: Any) -> bool:
        if not self._is_authenticated(request):
            return False

        if self._is_editor_or_admin(request):
            return True

        author_id = self._extract_owner_id(obj, "author_id")
        return author_id == getattr(request.user, "id", None)


class IsCommentAuthorOrAdmin(RolePermissionMixin, BasePermission):
    """Allow comment deletion/update for comment author or admin."""

    message = "Forbidden! Only comment author or admin can perform this action."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        return self._is_authenticated(request)

    def has_object_permission(self, request: DRFRequest, view: ViewSet, obj: Any) -> bool:
        if not self._is_authenticated(request):
            return False

        if self._is_admin(request):
            return True

        owner_id = self._extract_owner_id(obj, "user_id")
        return owner_id == getattr(request.user, "id", None)


class IsOwnerOrAdmin(RolePermissionMixin, BasePermission):
    """Allow action only for object owner or admin."""

    message = "Forbidden! You can modify only your own profile."

    def has_permission(self, request: DRFRequest, view: ViewSet) -> bool:
        return self._is_authenticated(request)

    def has_object_permission(self, request: DRFRequest, view: ViewSet, obj: Any) -> bool:
        if not self._is_authenticated(request):
            return False

        if self._is_admin(request):
            return True

        owner_id = self._extract_owner_id(obj, "id", "user_id")
        return owner_id == getattr(request.user, "id", None)