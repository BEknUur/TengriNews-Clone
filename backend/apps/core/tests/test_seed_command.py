import pytest
from django.core.management import call_command
from apps.accounts.models import CustomUser


@pytest.mark.django_db
def test_seed_command_runs_no_force(settings, capfd):
    # ensure tests run in a DEBUG context so the command does not require --force
    settings.DEBUG = True

    # call with no clear and small numbers
    call_command(
        "seed_data",
        "--users=1",
        "--categories=1",
        "--tags=1",
        "--articles=1",
        "--comments=1",
        "--noinput",
    )

    assert CustomUser.objects.filter(is_superuser=False).exists()