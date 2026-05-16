import pytest

from rest_framework.exceptions import ValidationError

from apps.accounts.serializers.serializers import RegistrationSerializer, LoginSerializer
from apps.accounts.serializers.serializers import UserSerializer
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_registration_password_mismatch():
    data = {
        "email": "new@example.test",
        "first_name": "A",
        "last_name": "B",
        "password": "password123",
        "password_confirm": "password321",
    }
    serializer = RegistrationSerializer(data=data)
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_registration_create_user(monkeypatch):
    data = {
        "email": "new2@example.test",
        "first_name": "A",
        "last_name": "B",
        "password": "password123",
        "password_confirm": "password123",
    }

    # prevent actual token generation
    class FakeToken:
        access_token = "access"

        def __str__(self):
            return "refresh"

    class FakeRefresh:
        access_token = "access"

        def __str__(self):
            return "refresh"

    monkeypatch.setattr("apps.accounts.serializers.serializers.RefreshToken.for_user", lambda u: FakeRefresh())

    serializer = RegistrationSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.pk is not None
    assert user.email == "new2@example.test"


@pytest.mark.django_db
def test_login_invalid_credentials(monkeypatch):
    monkeypatch.setattr("apps.accounts.serializers.serializers.authenticate", lambda **kwargs: None)
    data = {"email": "noone@example.test", "password": "pw"}
    serializer = LoginSerializer(data=data, context={})
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_login_disabled_account(monkeypatch):
    user = UserFactory(is_active=False)
    monkeypatch.setattr("apps.accounts.serializers.serializers.authenticate", lambda **kwargs: user)
    data = {"email": user.email, "password": "pw"}
    serializer = LoginSerializer(data=data, context={})
    with pytest.raises(ValidationError):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_login_success(monkeypatch):
    user = UserFactory(is_active=True)
    monkeypatch.setattr("apps.accounts.serializers.serializers.authenticate", lambda **kwargs: user)

    class FakeRefresh:
        access_token = "access"

        def __str__(self):
            return "refresh"

    monkeypatch.setattr("apps.accounts.serializers.serializers.RefreshToken.for_user", lambda u: FakeRefresh())

    data = {"email": user.email, "password": "pw"}
    serializer = LoginSerializer(data=data, context={})
    assert serializer.is_valid()
    out = serializer.validated_data
    assert "access" in out and "refresh" in out

@pytest.mark.django_db
def test_user_serializer_basic():
    u = UserFactory()
    data = UserSerializer(u).data
    assert data["email"] == u.email