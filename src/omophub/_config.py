"""Configuration management for the OMOPHub SDK."""

from __future__ import annotations

import os

# Default API configuration
DEFAULT_BASE_URL = "https://api.omophub.com/v1"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3

# Module-level configuration (can be overridden)
api_key: str | None = os.environ.get("OMOPHUB_API_KEY")
api_url: str = os.environ.get("OMOPHUB_API_URL", DEFAULT_BASE_URL)
timeout: float = float(os.environ.get("OMOPHUB_TIMEOUT", DEFAULT_TIMEOUT))
max_retries: int = int(os.environ.get("OMOPHUB_MAX_RETRIES", DEFAULT_MAX_RETRIES))
