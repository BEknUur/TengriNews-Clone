"""Serializers for JWT-based authentication (register / login)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    SerializerMethodField,
    Serializer,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser


class RegistrationSerializer(ModelSerializer):
    """Validate registration payload and create a new user."""

    password = CharField(min_length=8, write_only=True)
    password_confirm = CharField(min_length=8, write_only=True)
    tokens = SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields: list[str] = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "tokens",
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Ensure both password fields match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict[str, Any]) -> CustomUser:
        """Create and return a new user with a hashed password."""
        validated_data.pop("password_confirm")
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def get_tokens(self, obj: CustomUser) -> dict[str, str]:
        """Generate access and refresh JWT tokens for the user."""
        refresh = RefreshToken.for_user(obj)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class LoginSerializer(Serializer):
    """Validate credentials and return JWT tokens."""

    email = EmailField(write_only=True)
    password = CharField(write_only=True)
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Authenticate the user and attach tokens to attrs."""
        user: CustomUser | None = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise ValidationError({"email": "Invalid credentials."})
        if not user.is_active:
            raise ValidationError({"email": "Account is disabled."})
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
