# Django modules
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

# Third-party modules
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminEmailInputWidget

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
        "is_active",
        "is_staff",
    )

    list_filter = ("is_active", "is_staff")
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
                    "password1",
                    "password2",
                ),
            },
        ),
    )

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
