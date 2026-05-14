# Python modules
from typing import Any

# Django modules
from django.db.models import Model, DateTimeField
from django.utils import timezone as django_timezone


class AbstractTimeStamptModel(Model):
    """Abstract base model with created, updated, and soft-delete timestamp fields."""

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    deleted_at = DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Soft-delete by setting deleted_at to now instead of removing the row."""
        self.deleted_at = django_timezone.now()
        self.save(update_fields=["deleted_at"])
