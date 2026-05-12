# Third-party modules
from rest_framework import serializers


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
