"""Tests for the FHIR client interop helpers."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest


class TestGetFhirServerUrl:
    """``get_fhir_server_url`` returns the right base URL per FHIR version."""

    def test_default_r4(self) -> None:
        from omophub.fhir_interop import get_fhir_server_url

        assert get_fhir_server_url() == "https://fhir.omophub.com/fhir/r4"

    @pytest.mark.parametrize(
        "version,expected",
        [
            ("r4", "https://fhir.omophub.com/fhir/r4"),
            ("r4b", "https://fhir.omophub.com/fhir/r4b"),
            ("r5", "https://fhir.omophub.com/fhir/r5"),
            ("r6", "https://fhir.omophub.com/fhir/r6"),
        ],
    )
    def test_each_version(self, version: str, expected: str) -> None:
        from omophub.fhir_interop import get_fhir_server_url

        assert get_fhir_server_url(version) == expected  # type: ignore[arg-type]


class TestGetFhirpyClient:
    """``get_fhirpy_client`` is lazy and raises ImportError when missing."""

    def test_missing_fhirpy_raises_import_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When ``fhirpy`` is not installed, we raise with an install hint."""
        # Ensure any cached import is cleared.
        monkeypatch.setitem(sys.modules, "fhirpy", None)  # type: ignore[arg-type]
        from omophub.fhir_interop import get_fhirpy_client

        with pytest.raises(ImportError, match="pip install omophub\\[fhirpy\\]"):
            get_fhirpy_client("oh_test")

    def test_returns_sync_client_with_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When ``fhirpy`` is available, the stub is called with the right URL."""
        captured: dict[str, object] = {}

        def _fake_sync_client(
            *, url: str, authorization: str
        ) -> SimpleNamespace:
            captured["url"] = url
            captured["authorization"] = authorization
            return SimpleNamespace(url=url, authorization=authorization)

        fake_module = ModuleType("fhirpy")
        fake_module.SyncFHIRClient = _fake_sync_client  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "fhirpy", fake_module)

        from omophub.fhir_interop import get_fhirpy_client

        client = get_fhirpy_client("oh_abc", "r5")

        assert captured == {
            "url": "https://fhir.omophub.com/fhir/r5",
            "authorization": "Bearer oh_abc",
        }
        assert client.url == "https://fhir.omophub.com/fhir/r5"

    def test_async_variant(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """``get_async_fhirpy_client`` wires the async constructor similarly."""
        captured: dict[str, object] = {}

        def _fake_async_client(
            *, url: str, authorization: str
        ) -> SimpleNamespace:
            captured["url"] = url
            captured["authorization"] = authorization
            return SimpleNamespace(url=url, authorization=authorization)

        fake_module = ModuleType("fhirpy")
        fake_module.AsyncFHIRClient = _fake_async_client  # type: ignore[attr-defined]
        monkeypatch.setitem(sys.modules, "fhirpy", fake_module)

        from omophub.fhir_interop import get_async_fhirpy_client

        get_async_fhirpy_client("oh_abc")

        assert captured == {
            "url": "https://fhir.omophub.com/fhir/r4",
            "authorization": "Bearer oh_abc",
        }


class TestOMOPHubFhirServerUrlProperty:
    """``OMOPHub.fhir_server_url`` returns the r4 base URL."""

    def test_sync_property(self) -> None:
        from omophub import OMOPHub

        client = OMOPHub(api_key="oh_test")
        try:
            assert client.fhir_server_url == "https://fhir.omophub.com/fhir/r4"
        finally:
            client.close()

    def test_async_property(self) -> None:
        from omophub import AsyncOMOPHub

        client = AsyncOMOPHub(api_key="oh_test")
        assert client.fhir_server_url == "https://fhir.omophub.com/fhir/r4"
