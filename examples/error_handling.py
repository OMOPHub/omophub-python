#!/usr/bin/env python3
"""Examples of error handling with the OMOPHub SDK."""

import time

import omophub


def handle_not_found() -> None:
    """Handle concept not found errors."""
    print("=== Handling Not Found ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    try:
        # Try to get a non-existent concept
        concept = client.concepts.get(999999999)
        print(f"Found: {concept['concept_name']}")
    except omophub.NotFoundError as e:
        print(f"Concept not found: {e.message}")
        print(f"  Status code: {e.status_code}")
        if e.request_id:
            print(f"  Request ID: {e.request_id}")


def handle_authentication() -> None:
    """Handle authentication errors."""
    print("\n=== Handling Authentication Errors ===")

    try:
        # Try to use an invalid API key
        client = omophub.OMOPHub(api_key="invalid_key")
        client.concepts.get(201826)
    except omophub.AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        print(f"  Status code: {e.status_code}")


def handle_rate_limit() -> None:
    """Handle rate limit errors with retry."""
    print("\n=== Handling Rate Limits ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    for i in range(5):
        try:
            client.search.basic("diabetes")
            print(f"Request {i + 1} succeeded")
        except omophub.RateLimitError as e:
            print(f"Rate limited! Retry after {e.retry_after} seconds")
            if e.retry_after is not None:
                time.sleep(e.retry_after)
            else:
                time.sleep(1)  # Default wait


def handle_validation() -> None:
    """Handle validation errors."""
    print("\n=== Handling Validation Errors ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    try:
        # Try an invalid request
        client.search.basic("")  # Empty query
    except omophub.ValidationError as e:
        print(f"Validation error: {e.message}")
        if e.details:
            print(f"  Details: {e.details}")


def comprehensive_error_handling() -> None:
    """Demonstrate comprehensive error handling."""
    print("\n=== Comprehensive Error Handling ===")

    client = omophub.OMOPHub(api_key="oh_your_api_key")

    try:
        concept = client.concepts.get(201826)
        print(f"Success: {concept['concept_name']}")

    except omophub.AuthenticationError as e:
        # Handle auth errors (401, 403)
        print(f"Auth error: {e.message}")

    except omophub.NotFoundError as e:
        # Handle not found (404)
        print(f"Not found: {e.message}")

    except omophub.RateLimitError as e:
        # Handle rate limits (429)
        print(f"Rate limited, retry after: {e.retry_after}s")

    except omophub.ValidationError as e:
        # Handle bad requests (400)
        print(f"Invalid request: {e.message}")

    except omophub.ServerError as e:
        # Handle server errors (5xx)
        print(f"Server error: {e.message}")

    except omophub.ConnectionError as e:
        # Handle network issues
        print(f"Connection error: {e.message}")

    except omophub.TimeoutError as e:
        # Handle timeouts
        print(f"Request timed out: {e.message}")

    except omophub.OMOPHubError as e:
        # Catch-all for any SDK error
        print(f"SDK error: {e.message}")


if __name__ == "__main__":
    handle_not_found()
    handle_authentication()
    # handle_rate_limit()  # Uncomment to test rate limiting
    handle_validation()
    comprehensive_error_handling()
