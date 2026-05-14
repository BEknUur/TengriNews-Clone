# Python modules
from typing import Any

# Third-party modules
import pytest
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response as DRFResponse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ViewSet

# Project modules
from apps.core.decorators import require_permissions
from apps.core.mixins import ViewSetWorkflowMixin
from apps.main.models import Category
from apps.main.serializers import CategorySerializer


class PermissionCheckViewSet(ViewSet):
    """PermissionCheckViewSet class."""

    permission_classes = [AllowAny]
    throttle_classes = []

    @require_permissions(IsAuthenticated)
    def list(self, request: Any) -> Any:
        return DRFResponse({"detail": "ok"}, status=HTTP_200_OK)


class WorkflowTestViewSet(ViewSet, ViewSetWorkflowMixin):
    permission_classes = [AllowAny]
    throttle_classes = []

    def retrieve(self, request: Any, pk: Any = None) -> Any:
        obj, error_response = self.get_object_or_404_response(Category.objects, pk=pk)
        if error_response:
            return error_response

        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=obj,
            status_code=HTTP_200_OK,
        )

    def create(self, request: Any) -> Any:
        """Create and return a new instance from validated data."""
        serializer = self.validate_request_serializer(
            CategorySerializer, request=request
        )
        category = serializer.save()
        return self.serialize_to_response(
            serializer_class=CategorySerializer,
            instance=category,
            status_code=HTTP_201_CREATED,
        )


@pytest.mark.django_db
class TestRequirePermissionsDecorator:
    """TestRequirePermissionsDecorator class."""

    def test_returns_401_for_unauthenticated_request(self) -> None:
        """Test `test_returns_401_for_unauthenticated_request`."""
        request = APIRequestFactory().get("/permission-check/")
        view = PermissionCheckViewSet.as_view({"get": "list"})

        response = view(request)

        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_returns_200_for_authenticated_request(self, user: Any) -> None:
        """Test `test_returns_200_for_authenticated_request`."""
        request = APIRequestFactory().get("/permission-check/")
        force_authenticate(request, user=user)
        view = PermissionCheckViewSet.as_view({"get": "list"})

        response = view(request)

        assert response.status_code == HTTP_200_OK


@pytest.mark.django_db
class TestViewSetWorkflowMixin:
    """TestViewSetWorkflowMixin class."""

    def test_get_object_or_404_response_returns_not_found_payload(self) -> None:
        """Test `test_get_object_or_404_response_returns_not_found_payload`."""
        request = APIRequestFactory().get("/workflow/9999/")
        view = WorkflowTestViewSet.as_view({"get": "retrieve"})

        response = view(request, pk="9999")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert response.data == {"detail": "Not found."}

    def test_validate_request_serializer_and_serialize_response(self) -> None:
        """Test `test_validate_request_serializer_and_serialize_response`."""
        request = APIRequestFactory().post(
            "/workflow/",
            {"name": "Science", "slug": "science"},
            format="json",
        )
        view = WorkflowTestViewSet.as_view({"post": "create"})

        response = view(request)

        assert response.status_code == HTTP_201_CREATED
        assert response.data["name"] == "Science"
        assert response.data["slug"] == "science"
