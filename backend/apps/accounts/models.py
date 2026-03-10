# Django modules
from django.db.models import (
    CharField,
    EmailField,
    BooleanField,
    DateTimeField,
    ImageField,
)
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

# Project modules
from apps.abstract.models import AbstractTimeStamptModel
from apps.accounts.manager import CustomUserManager


# Constants
FIRST_NAME_MAX_LENGTH = 50
LAST_NAME_MAX_LENGTH = 50
ROLE_MAX_LENGTH = 50




class CustomUser(
    AbstractBaseUser,
    PermissionsMixin,
    AbstractTimeStamptModel,
):
    """
    Custom User Model that
    extends AbstractBaseUser, PermissionsMixin,
    and AbstractTimeStamptModel

    Fields:
        - email: EmailField

        - first_name: CharField
        - last_name: CharField
        - role:CharField

        - is_active: BooleanField
        - is_staff: BooleanField

        - date_joined: DateTimeField
        - avatar: ImageField

        - created_at: DateTimeField
        - updated_at: DateTimeField
        - deleted_at: DateTimeField


    Methods:
        - __str__: Return a string representation of the user
    """

    ADMIN="ADMIN"
    USER="USER"
    EDITOR="EDITOR"

    ROLE_CHOICES = [
        (ADMIN, "ADMIN"),
        (USER, "USER"),
        (EDITOR, "EDITOR"),
    ]


    email = EmailField(
        unique=True,
    )

    first_name = CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
    )
    last_name = CharField(
        max_length=LAST_NAME_MAX_LENGTH,
    )
    role = CharField(
        max_length=ROLE_MAX_LENGTH,
        choices=ROLE_CHOICES,
        default=USER,
    )

    is_active = BooleanField(
        default=True,
    )
    is_staff = BooleanField(
        default=False,
    )

    date_joined = DateTimeField(
        auto_now_add=True,
    )

    avatar = ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "user"

    def __str__(self):
        return f"Email: {self.email}, Fullname: {self.first_name} {self.last_name}"
