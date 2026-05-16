import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.conf import settings

@pytest.mark.django_db
def test_seed_command_refuses_on_production(monkeypatch):
    # Simulate DEBUG=False
    monkeypatch.setattr(settings, "DEBUG", False)
    with pytest.raises(CommandError):
        call_command("seed_data", "--users=1")

@pytest.mark.django_db
def test_seed_command_force_overrides(monkeypatch):
    # When DEBUG=False but --force provided, command should run without exiting
    monkeypatch.setattr(settings, "DEBUG", False)
    # Should not raise
    call_command("seed_data", "--users=1", "--force", "--noinput")
