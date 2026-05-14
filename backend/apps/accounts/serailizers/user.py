"""Serializers for the CustomUser model."""

from __future__ import annotations

from rest_framework.serializers import ModelSerializer

from apps.accounts.models import CustomUser


class UserSerializer(ModelSerializer):
    """Read-only serializer that exposes public user fields."""

    class Meta:
        model = CustomUser
        fields: tuple[str, ...] = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "preferred_language",
            "avatar",
            "is_staff",
            "is_superuser",
            "created_at",
        )
        read_only_fields = fields


class UserUpdateSerializer(ModelSerializer):
    """Serializer for partial user-profile updates."""

    class Meta:
        model = CustomUser
        fields: tuple[str, ...] = ("first_name", "last_name", "preferred_language", "avatar")
