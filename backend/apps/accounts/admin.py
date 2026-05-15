# Django modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Third-party modules - optional
try:
    from unfold.admin import ModelAdmin
    from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
    from unfold.widgets import UnfoldAdminEmailInputWidget, UnfoldAdminTextInputWidget
except Exception:  # pragma: no cover - optional admin enhancements
    ModelAdmin = object
    AdminPasswordChangeForm = None
    UserChangeForm = None
    UserCreationForm = None
    UnfoldAdminEmailInputWidget = None
    UnfoldAdminTextInputWidget = None

# Project modules
from apps.accounts.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "preferred_language",
        "is_active",
        "is_staff",
        "created_at",
    )

    list_filter = ("is_active", "is_staff", "role")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal Info"),
            {
                "fields": (
                    ("first_name", "last_name"),
                    "avatar",
                    "preferred_language",
                    "role",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["collapse"],
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login",),
                "classes": ["collapse"],
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "preferred_language",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Only apply custom widgets when unfold is available
    if UnfoldAdminEmailInputWidget and UnfoldAdminTextInputWidget:
        formfield_overrides = {
            CustomUser._meta.get_field("email").__class__: {
                "widget": UnfoldAdminEmailInputWidget
            },
            CustomUser._meta.get_field("first_name").__class__: {
                "widget": UnfoldAdminTextInputWidget
            },
            CustomUser._meta.get_field("last_name").__class__: {
                "widget": UnfoldAdminTextInputWidget
            },
        }
