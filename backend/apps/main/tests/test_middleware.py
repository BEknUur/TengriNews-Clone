# Python modules
import json
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
            record.message
            for record in caplog.records
            if "request_finished" in record.message
        ]
        assert records

        payload = json.loads(records[-1])
        assert payload["event"] == "request_finished"
        assert payload["method"] == "GET"
        assert payload["path"] == "/api/articles/"
        assert payload["status_code"] == 200
        assert "duration_ms" in payload
        assert "ip" in payload
    finally:
        logger.removeHandler(caplog.handler)
