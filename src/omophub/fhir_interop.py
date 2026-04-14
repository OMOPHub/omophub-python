"""FHIR client interop helpers for the OMOPHub FHIR Terminology Service.

These helpers make it easy to point an external FHIR client library
(`fhirpy`, `fhir.resources`, or any httpx-based client) at OMOPHub's
FHIR endpoint. None of the optional FHIR client libraries are required
dependencies of the SDK; import errors are raised lazily when the
helper is actually called.

Example:
    >>> from omophub.fhir_interop import get_fhirpy_client
    >>> fhir = get_fhirpy_client("oh_xxxxxxxxx")
    >>> bundle = fhir.resources("CodeSystem").search(
    ...     url="http://snomed.info/sct"
    ... ).fetch()
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    FhirVersion = Literal["r4", "r4b", "r5", "r6"]

_FHIR_BASE = "https://fhir.omophub.com/fhir"


def get_fhir_server_url(version: FhirVersion = "r4") -> str:
    """Return the OMOPHub FHIR Terminology Service base URL.

    Args:
        version: FHIR version prefix - one of ``"r4"`` (default),
                 ``"r4b"``, ``"r5"``, or ``"r6"``.

    Returns:
        Full base URL, e.g. ``"https://fhir.omophub.com/fhir/r4"``.
    """
    return f"{_FHIR_BASE}/{version}"


def get_fhirpy_client(api_key: str, version: FhirVersion = "r4") -> Any:
    """Return a ``fhirpy.SyncFHIRClient`` pre-configured for OMOPHub.

    Requires the ``fhirpy`` package. Install with::

        pip install omophub[fhirpy]

    Args:
        api_key: OMOPHub API key (``oh_...``).
        version: FHIR version prefix.

    Returns:
        A ``SyncFHIRClient`` instance pointed at OMOPHub with the
        ``Authorization: Bearer <api_key>`` header pre-attached.

    Raises:
        ImportError: if ``fhirpy`` is not installed.
    """
    try:
        # `fhirpy` is an optional extra; mypy's per-module caching means
        # only one of the two conditional imports in this file is flagged
        # with `import-not-found`, depending on order, so we silence both
        # and pair with `unused-ignore` to keep `warn_unused_ignores` happy.
        from fhirpy import (  # type: ignore[import-not-found, unused-ignore]
            SyncFHIRClient,
        )
    except ImportError as e:  # pragma: no cover - import guard
        raise ImportError(
            "fhirpy is required for FHIR client interop. "
            "Install with: pip install omophub[fhirpy]"
        ) from e
    return SyncFHIRClient(
        url=get_fhir_server_url(version),
        authorization=f"Bearer {api_key}",
    )


def get_async_fhirpy_client(api_key: str, version: FhirVersion = "r4") -> Any:
    """Return a ``fhirpy.AsyncFHIRClient`` pre-configured for OMOPHub.

    Async counterpart of :func:`get_fhirpy_client`. Same install hint.
    """
    try:
        from fhirpy import (  # type: ignore[import-not-found, unused-ignore]
            AsyncFHIRClient,
        )
    except ImportError as e:  # pragma: no cover - import guard
        raise ImportError(
            "fhirpy is required for FHIR client interop. "
            "Install with: pip install omophub[fhirpy]"
        ) from e
    return AsyncFHIRClient(
        url=get_fhir_server_url(version),
        authorization=f"Bearer {api_key}",
    )


__all__ = [
    "get_async_fhirpy_client",
    "get_fhir_server_url",
    "get_fhirpy_client",
]
