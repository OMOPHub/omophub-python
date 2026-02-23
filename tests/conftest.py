"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
import time
from typing import Any

import pytest

# Load .env file for integration tests
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on environment variables

import omophub

# Mock API key for tests
TEST_API_KEY = "oh_test_key_12345"


@pytest.fixture
def api_key() -> str:
    """Provide test API key."""
    return TEST_API_KEY


@pytest.fixture
def base_url() -> str:
    """Provide test base URL."""
    return "https://api.omophub.com/v1"


@pytest.fixture
def sync_client(api_key: str) -> omophub.OMOPHub:
    """Create a synchronous client for testing."""
    return omophub.OMOPHub(api_key=api_key)


@pytest.fixture
async def async_client(api_key: str) -> omophub.AsyncOMOPHub:
    """Create an async client for testing."""
    client = omophub.AsyncOMOPHub(api_key=api_key)
    yield client
    await client.close()


@pytest.fixture
def mock_concept() -> dict[str, Any]:
    """Provide a mock concept response."""
    return {
        "concept_id": 201826,
        "concept_name": "Type 2 diabetes mellitus",
        "domain_id": "Condition",
        "vocabulary_id": "SNOMED",
        "concept_class_id": "Clinical Finding",
        "standard_concept": "S",
        "concept_code": "44054006",
        "valid_start_date": "1970-01-01",
        "valid_end_date": "2099-12-31",
        "invalid_reason": None,
    }


@pytest.fixture
def mock_vocabulary() -> dict[str, Any]:
    """Provide a mock vocabulary response."""
    return {
        "vocabulary_id": "SNOMED",
        "vocabulary_name": "SNOMED CT",
        "vocabulary_version": "2024-03-01",
        "vocabulary_concept_id": 44819096,
        "concept_count": 485000,
    }


@pytest.fixture
def mock_api_response(mock_concept: dict[str, Any]) -> dict[str, Any]:
    """Provide a mock API response wrapper."""
    return {
        "success": True,
        "data": mock_concept,
        "meta": {
            "request_id": "req_test123",
            "timestamp": "2024-12-01T00:00:00Z",
            "vocab_release": "2024.2",
        },
    }


@pytest.fixture
def mock_paginated_response() -> dict[str, Any]:
    """Provide a mock paginated API response."""
    return {
        "success": True,
        "data": {
            "concepts": [
                {
                    "concept_id": 201826,
                    "concept_name": "Type 2 diabetes mellitus",
                    "vocabulary_id": "SNOMED",
                    "concept_code": "44054006",
                    "domain_id": "Condition",
                    "concept_class_id": "Clinical Finding",
                    "standard_concept": "S",
                },
            ],
        },
        "meta": {
            "request_id": "req_test123",
            "pagination": {
                "page": 1,
                "page_size": 20,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
        },
    }


@pytest.fixture
def mock_error_response() -> dict[str, Any]:
    """Provide a mock error response."""
    return {
        "success": False,
        "error": {
            "code": "not_found",
            "message": "Concept not found",
            "details": {"concept_id": 999999999},
        },
    }


@pytest.fixture(autouse=True)
def rate_limit_delay(request: pytest.FixtureRequest) -> None:
    """Add delay between integration tests to avoid rate limiting."""
    yield
    # Only delay for integration tests
    if "integration" in request.keywords:
        time.sleep(2)


# Well-known test concept IDs for integration tests
DIABETES_CONCEPT_ID = 201826  # Type 2 diabetes mellitus (SNOMED)
ASPIRIN_CONCEPT_ID = 1112807  # Aspirin (RxNorm)
MI_CONCEPT_ID = 4329847  # Myocardial infarction (SNOMED)
HYPERTENSION_CONCEPT_ID = 316866  # Hypertensive disorder (SNOMED)


def extract_data(result: dict[str, Any] | list[Any], key: str) -> list[Any]:
    """Safely extract data from wrapped API response.

    Handles both old format (direct array) and new format (wrapped in named key).
    For batch endpoints, also handles 'results' key as fallback for backward
    compatibility with production API during transition period.

    Args:
        result: API response, either a list or dict with named key
        key: The key to extract (e.g., 'concepts', 'vocabularies', 'suggestions')

    Returns:
        The extracted list of items, always a list
    """
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        value = result.get(key)
        if isinstance(value, list):
            return value
        # Handle nested dicts: {"results": {"results": [...]}}
        if isinstance(value, dict) and key in value:
            nested = value.get(key)
            if isinstance(nested, list):
                return nested
        # Fallback: check 'results' key for batch endpoint backward compatibility
        # (production API returns 'results', new API will return 'concepts')
        if key == "concepts":
            fallback = result.get("results")
            if isinstance(fallback, list):
                return fallback
        # Key not found or not a list, return empty list
        return []
    # Unexpected type, return empty list
    return []


def get_integration_api_key() -> str | None:
    """Get API key for integration tests from environment."""
    # Check TEST_API_KEY first (explicit test key), then OMOPHUB_API_KEY
    return os.environ.get("TEST_API_KEY") or os.environ.get("OMOPHUB_API_KEY")


@pytest.fixture
def integration_client() -> omophub.OMOPHub:
    """Real API client for integration tests.

    Requires TEST_API_KEY or OMOPHUB_API_KEY environment variable.
    """
    api_key = get_integration_api_key()
    if not api_key:
        pytest.skip("TEST_API_KEY or OMOPHUB_API_KEY not set")
    client = omophub.OMOPHub(api_key=api_key)
    yield client
    client.close()


@pytest.fixture
async def async_integration_client() -> omophub.AsyncOMOPHub:
    """Async real API client for integration tests.

    Requires TEST_API_KEY or OMOPHUB_API_KEY environment variable.
    """
    api_key = get_integration_api_key()
    if not api_key:
        pytest.skip("TEST_API_KEY or OMOPHUB_API_KEY not set")
    client = omophub.AsyncOMOPHub(api_key=api_key)
    yield client
    await client.close()


# Skip integration tests unless API key is set
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring real API",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip integration tests if no API key is set."""
    if not get_integration_api_key():
        skip_integration = pytest.mark.skip(
            reason="TEST_API_KEY or OMOPHUB_API_KEY not set for integration tests"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
