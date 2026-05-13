# Third-party modules
from rest_framework import serializers


class TokenPairResponseSerializer(serializers.Serializer):
    """Schema for access/refresh token pair response payload."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class LoginRequestSerializer(serializers.Serializer):
    """Schema for login request payload."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)


class RegisterRequestSerializer(serializers.Serializer):
    """Schema for register request payload."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)


class RegisterResponseSerializer(serializers.Serializer):
    """Schema for register response payload."""

    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    tokens = TokenPairResponseSerializer(read_only=True)


class RefreshTokenRequestSerializer(serializers.Serializer):
    """Schema for refresh-token request payload."""

    refresh = serializers.CharField()


class AccessTokenResponseSerializer(serializers.Serializer):
    """Schema for access-token response payload."""

    access = serializers.CharField(read_only=True)
