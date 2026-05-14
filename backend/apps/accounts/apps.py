# Python modules
from typing import Any

# Django modules
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """AccountsConfig class."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self) -> Any:
        """Initialize app-level integrations when Django starts this app."""
        from unfold.templatetags import unfold as unfold_tags

        def safe_flatten_context(context: Any) -> Any:
            """Safely flatten template context layers into a plain dictionary."""
            keys = set()
            for layer in context.dicts:
                if hasattr(layer, "keys"):
                    keys.update(layer.keys())
            return {key: context[key] for key in keys}

        unfold_tags._flatten_context = safe_flatten_context
