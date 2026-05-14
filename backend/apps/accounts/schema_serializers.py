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


class UserResponseSerializer(serializers.Serializer):
    """Schema for user response payload."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(read_only=True, allow_null=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class UserCreateRequestSerializer(serializers.Serializer):
    """Schema for user create request payload."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    role = serializers.CharField(required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)


class UserPatchRequestSerializer(serializers.Serializer):
    """Schema for user partial update request payload."""

    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)
