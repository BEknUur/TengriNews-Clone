# Python modules
from typing import Any
import logging

# Django modules
from django.db import transaction

# Third-party modules
from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

# Project modules
from apps.accounts.auth.serializers import RegistrationSerializer, LoginSerializer
from apps.abstracts.decorators import validate_serializer_data
from apps.abstracts.mixins import DRFResponseMixin
from apps.abstracts.trottling import CustomAnonRateThrottle, CustomUserRateThrottle
from apps.accounts.tasks import send_welcome_email_task

logger = logging.getLogger(__name__)


class AuthViewSet(DRFResponseMixin, ViewSet):
    """
    ViewSet for Authentication
    """

    permission_classes = [AllowAny]
    throttle_classes = [
        CustomAnonRateThrottle,
        CustomUserRateThrottle,
        ScopedRateThrottle,
    ]

    def get_throttles(self):
        """Assign scoped throttle rates for login/register actions."""
        if self.action == "login":
            self.throttle_scope = "auth_login"
        elif self.action == "register":
            self.throttle_scope = "auth_register"
        return super().get_throttles()

    @extend_schema(request=LoginSerializer, responses={200: LoginSerializer})
    @action(
        methods=("POST",),
        detail=False,
        url_path="token",
        url_name="token",
    )
    @validate_serializer_data(serializer_class=LoginSerializer)
    def login(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        email = request.data.get("email", "N/A")
        logger.info(f"Login attempt: email={email}")
        logger.info(f"Login successful: email={email}")
        return DRFResponse(
            data=kwargs["validated_data"],
            status=HTTP_200_OK,
        )

    @extend_schema(
        request=RegistrationSerializer, responses={201: RegistrationSerializer}
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="register",
        url_name="register",
    )
    @validate_serializer_data(serializer_class=RegistrationSerializer)
    def register(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        email = request.data.get("email", "N/A")
        logger.info(f"Registration attempt: email={email}")
        serializer: RegistrationSerializer = kwargs["serializer"]
        user = serializer.save()

        transaction.on_commit(lambda: send_welcome_email_task.delay(user.id))

        logger.info(f"Registration successful: user_id={user.id}, email={email}")
        return self.get_drf_response(
            request=request,
            data=user,
            serializer_class=RegistrationSerializer,
            status_code=HTTP_201_CREATED,
        )

    @extend_schema(
        request=TokenRefreshSerializer, responses={200: TokenRefreshSerializer}
    )
    @action(
        methods=("POST",),
        detail=False,
        url_path="token/refresh",
        url_name="refresh",
    )
    def token(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> DRFResponse:
        logger.info("Token refresh attempt")
        serializer: TokenRefreshSerializer = TokenRefreshSerializer(
            data=request.data,
        )
        try:
            if serializer.is_valid():
                logger.info("Token refresh successful")
                return DRFResponse(
                    data=serializer.validated_data,
                    status=HTTP_200_OK,
                )
        except TokenError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise InvalidToken(e.args[0])

        logger.warning(f"Token refresh validation failed: {serializer.errors}")
        return DRFResponse(
            data=serializer.errors,
            status=HTTP_400_BAD_REQUEST,
        )
