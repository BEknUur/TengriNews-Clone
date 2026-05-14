from __future__ import annotations

# Django modules
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ImageField,
    TextChoices,
)

# Project modules
from apps.core.models import AbstractTimeStamptModel
from apps.accounts.manager import CustomUserManager

# Constants
FIRST_NAME_MAX_LENGTH: int = 50
LAST_NAME_MAX_LENGTH: int = 50
ROLE_MAX_LENGTH: int = 10


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractTimeStamptModel):
    """Application user identified by email address.

    Fields:
        email: unique login identifier.
        first_name / last_name: display name parts.
        role: ADMIN | EDITOR | USER.
        is_active / is_staff: standard Django flags.
        date_joined: set automatically on creation.
        avatar: optional profile picture.
    """

    class Role(TextChoices):
        """Role class."""
        ADMIN = "ADMIN", "Admin"
        EDITOR = "EDITOR", "Editor"
        USER = "USER", "User"

    email = EmailField(unique=True)
    first_name = CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = CharField(max_length=LAST_NAME_MAX_LENGTH)
    role = CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
    )
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    date_joined = DateTimeField(auto_now_add=True)
    avatar = ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        """Meta class."""
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        """Return a human-readable string representation of this object."""
        return self.email

    def __repr__(self) -> str:
        """Return a developer-friendly representation of this object."""
        return f"CustomUser(id={self.pk}, email={self.email!r})"
