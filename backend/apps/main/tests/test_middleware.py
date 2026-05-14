# Python modules
import logging
from typing import Any

# Third-party modules
import pytest


@pytest.mark.django_db
def test_structured_logging_middleware_logs_request(auth_client: Any, caplog: Any) -> None:
    """Test `test_structured_logging_middleware_logs_request`."""
    logger = logging.getLogger("apps.requests")
    logger.addHandler(caplog.handler)

    try:
        caplog.set_level(logging.INFO, logger="apps.requests")

        response = auth_client.get("/api/articles/")

        assert response.status_code == 200
        assert "X-Request-ID" in response

        records = [
            record
            for record in caplog.records
            if getattr(record, "event", None) == "request_finished"
        ]
        assert records, "No request_finished log record found"

        record = records[-1]
        assert record.event == "request_finished"
        assert record.method == "GET"
        assert record.path == "/api/articles/"
        assert record.status_code == 200
        assert hasattr(record, "duration_ms")
        assert hasattr(record, "ip")
    finally:
        logger.removeHandler(caplog.handler)
