# Third-party modules
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


# Custom throttling classes
class CustomAnonRateThrottle(AnonRateThrottle):
    """Custom throttle for anonymous users."""

    scope = "anon"


class CustomUserRateThrottle(UserRateThrottle):
    """Custom throttle for authenticated users."""

    scope = "user"
