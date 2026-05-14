# Django modules
from django.apps import AppConfig


class MainConfig(AppConfig):
    """MainConfig class."""
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.main"

    def ready(self) -> None:
        """Initialize app-level integrations when Django starts this app."""
        from . import signals  # noqa: F401
