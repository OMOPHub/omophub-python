"""Tests for SDK exceptions."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from omophub import (
    AuthenticationError,
    NotFoundError,
    OMOPHub,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestExceptions:
    """Tests for exception handling."""

    @respx.mock
    def test_not_found_error(
        self, sync_client: OMOPHub, mock_error_response: dict, base_url: str
    ) -> None:
        """Test 404 raises NotFoundError."""
        respx.get(f"{base_url}/concepts/999999999").mock(
            return_value=Response(404, json=mock_error_response)
        )

        with pytest.raises(NotFoundError) as exc_info:
            sync_client.concepts.get(999999999)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.message.lower()

    @respx.mock
    def test_authentication_error(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test 401 raises AuthenticationError."""
        error_response = {
            "success": False,
            "error": {
                "code": "unauthorized",
                "message": "Invalid API key",
            },
        }
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(401, json=error_response)
        )

        with pytest.raises(AuthenticationError) as exc_info:
            sync_client.concepts.get(201826)

        assert exc_info.value.status_code == 401

    @respx.mock
    def test_validation_error(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test 400 raises ValidationError."""
        error_response = {
            "success": False,
            "error": {
                "code": "validation_error",
                "message": "Invalid parameter",
            },
        }
        respx.get(f"{base_url}/search/concepts").mock(
            return_value=Response(400, json=error_response)
        )

        with pytest.raises(ValidationError) as exc_info:
            sync_client.search.basic("")

        assert exc_info.value.status_code == 400

    @respx.mock
    def test_rate_limit_error(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test 429 raises RateLimitError with retry_after."""
        error_response = {
            "success": False,
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Too many requests",
            },
        }
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(
                429,
                json=error_response,
                headers={"Retry-After": "60"},
            )
        )

        with pytest.raises(RateLimitError) as exc_info:
            sync_client.concepts.get(201826)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    @respx.mock
    def test_server_error(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test 500 raises ServerError."""
        error_response = {
            "success": False,
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
            },
        }
        respx.get(f"{base_url}/concepts/201826").mock(
            return_value=Response(500, json=error_response)
        )

        with pytest.raises(ServerError) as exc_info:
            sync_client.concepts.get(201826)

        assert exc_info.value.status_code == 500


class TestAPIErrorStringRepresentation:
    """Tests for APIError __str__ method."""

    def test_api_error_str_with_request_id(self) -> None:
        """Test APIError string includes request_id when present."""
        from omophub._exceptions import APIError

        error = APIError(
            "Test error message",
            status_code=400,
            request_id="req_abc123",
        )

        error_str = str(error)
        assert "Test error message" in error_str
        assert "status=400" in error_str
        assert "request_id=req_abc123" in error_str

    def test_api_error_str_with_error_code(self) -> None:
        """Test APIError stores error_code properly."""
        from omophub._exceptions import APIError

        error = APIError(
            "Validation failed",
            status_code=400,
            error_code="validation_error",
        )

        assert error.error_code == "validation_error"
        assert error.status_code == 400
        # error_code is stored but not in __str__ output
        error_str = str(error)
        assert "Validation failed" in error_str

    def test_api_error_str_minimal(self) -> None:
        """Test APIError string with only required fields."""
        from omophub._exceptions import APIError

        error = APIError("Simple error", status_code=500)

        error_str = str(error)
        assert "Simple error" in error_str
        assert "status=500" in error_str
        assert "request_id" not in error_str

    def test_api_error_with_details(self) -> None:
        """Test APIError stores details dictionary."""
        from omophub._exceptions import APIError

        details = {"field": "concept_id", "reason": "must be positive"}
        error = APIError(
            "Validation error",
            status_code=400,
            details=details,
        )

        assert error.details == details
        assert error.details["field"] == "concept_id"


class TestConnectionAndTimeoutErrors:
    """Tests for ConnectionError and TimeoutError."""

    def test_connection_error_creation(self) -> None:
        """Test ConnectionError can be created and has message."""
        from omophub._exceptions import ConnectionError

        error = ConnectionError("Failed to connect to server")

        assert error.message == "Failed to connect to server"
        assert str(error) == "Failed to connect to server"

    def test_timeout_error_creation(self) -> None:
        """Test TimeoutError can be created and has message."""
        from omophub._exceptions import TimeoutError

        error = TimeoutError("Request timed out after 30 seconds")

        assert error.message == "Request timed out after 30 seconds"
        assert str(error) == "Request timed out after 30 seconds"

    def test_connection_error_inheritance(self) -> None:
        """Test ConnectionError inherits from OMOPHubError."""
        from omophub._exceptions import ConnectionError, OMOPHubError

        error = ConnectionError("Network error")

        assert isinstance(error, OMOPHubError)
        assert isinstance(error, Exception)

    def test_timeout_error_inheritance(self) -> None:
        """Test TimeoutError inherits from OMOPHubError."""
        from omophub._exceptions import OMOPHubError, TimeoutError

        error = TimeoutError("Timeout")

        assert isinstance(error, OMOPHubError)
        assert isinstance(error, Exception)


class TestRaiseForStatus:
    """Tests for raise_for_status helper function."""

    def test_raise_for_status_400(self) -> None:
        """Test raise_for_status raises ValidationError for 400."""
        from omophub._exceptions import ValidationError, raise_for_status

        with pytest.raises(ValidationError) as exc_info:
            raise_for_status(400, "Bad request")

        assert exc_info.value.status_code == 400

    def test_raise_for_status_401(self) -> None:
        """Test raise_for_status raises AuthenticationError for 401."""
        from omophub._exceptions import AuthenticationError, raise_for_status

        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_status(401, "Unauthorized")

        assert exc_info.value.status_code == 401

    def test_raise_for_status_403(self) -> None:
        """Test raise_for_status raises AuthenticationError for 403."""
        from omophub._exceptions import AuthenticationError, raise_for_status

        with pytest.raises(AuthenticationError) as exc_info:
            raise_for_status(403, "Forbidden")

        assert exc_info.value.status_code == 403

    def test_raise_for_status_404(self) -> None:
        """Test raise_for_status raises NotFoundError for 404."""
        from omophub._exceptions import NotFoundError, raise_for_status

        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(404, "Not found")

        assert exc_info.value.status_code == 404

    def test_raise_for_status_429_with_retry_after(self) -> None:
        """Test raise_for_status raises RateLimitError with retry_after."""
        from omophub._exceptions import RateLimitError, raise_for_status

        with pytest.raises(RateLimitError) as exc_info:
            raise_for_status(429, "Rate limited", retry_after=60)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_raise_for_status_500(self) -> None:
        """Test raise_for_status raises ServerError for 500."""
        from omophub._exceptions import ServerError, raise_for_status

        with pytest.raises(ServerError) as exc_info:
            raise_for_status(500, "Internal server error")

        assert exc_info.value.status_code == 500

    def test_raise_for_status_502(self) -> None:
        """Test raise_for_status raises ServerError for 502."""
        from omophub._exceptions import ServerError, raise_for_status

        with pytest.raises(ServerError) as exc_info:
            raise_for_status(502, "Bad gateway")

        assert exc_info.value.status_code == 502

    def test_raise_for_status_unknown_4xx(self) -> None:
        """Test raise_for_status raises APIError for unknown 4xx codes."""
        from omophub._exceptions import APIError, raise_for_status

        with pytest.raises(APIError) as exc_info:
            raise_for_status(418, "I'm a teapot")

        assert exc_info.value.status_code == 418

    def test_raise_for_status_with_all_params(self) -> None:
        """Test raise_for_status passes all parameters to exception."""
        from omophub._exceptions import NotFoundError, raise_for_status

        with pytest.raises(NotFoundError) as exc_info:
            raise_for_status(
                404,
                "Concept not found",
                request_id="req_xyz789",
                error_code="concept_not_found",
                details={"concept_id": 99999},
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.request_id == "req_xyz789"
        assert exc_info.value.error_code == "concept_not_found"
        assert exc_info.value.details == {"concept_id": 99999}
