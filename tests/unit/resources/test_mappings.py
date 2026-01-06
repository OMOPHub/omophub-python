"""Tests for the mappings resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestMappingsResource:
    """Tests for the synchronous Mappings resource."""

    @respx.mock
    def test_get_mappings(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting mappings for a concept."""
        mappings_response = {
            "success": True,
            "data": {
                "mappings": [
                    {
                        "source_concept_id": 201826,
                        "target_concept_id": 45000001,
                        "mapping_type": "MAPS TO",
                        "target_vocabulary_id": "ICD10CM",
                    }
                ],
                "summary": {"total_mappings": 1},
            },
        }
        respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json=mappings_response)
        )

        result = sync_client.mappings.get(201826)
        assert "mappings" in result

    @respx.mock
    def test_get_mappings_with_filters(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting mappings with filter options."""
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        sync_client.mappings.get(
            201826,
            target_vocabulary="ICD10CM",
            include_invalid=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "target_vocabulary=ICD10CM" in url_str
        assert "include_invalid=true" in url_str

    @respx.mock
    def test_map_concepts(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test mapping concepts to a target vocabulary."""
        map_response = {
            "success": True,
            "data": {
                "mappings": [
                    {
                        "source": {"concept_id": 201826},
                        "target": {"concept_id": 45000001, "vocabulary_id": "ICD10CM"},
                    }
                ],
                "summary": {"mapped": 1, "failed": 0},
            },
        }
        route = respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json=map_response)
        )

        result = sync_client.mappings.map(
            source_concepts=[{"concept_id": 201826}],
            target_vocabulary="ICD10CM",
        )

        assert "mappings" in result
        # Verify request body was sent
        assert route.calls[0].request.content

    @respx.mock
    def test_map_concepts_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test mapping concepts with additional options."""
        route = respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        sync_client.mappings.map(
            source_concepts=[
                {"concept_id": 201826},
                {"vocabulary_id": "SNOMED", "concept_code": "44054006"},
            ],
            target_vocabulary="ICD10CM",
            mapping_type="equivalent",
            include_invalid=True,
        )

        # Verify POST body
        assert route.calls[0].request.content


class TestAsyncMappingsResource:
    """Tests for the asynchronous AsyncMappings resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_mappings(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting mappings."""
        respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        result = await async_client.mappings.get(201826)
        assert "mappings" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_mappings_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async mappings with filters."""
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        await async_client.mappings.get(
            201826,
            target_vocabulary="ICD10CM",
            include_invalid=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "target_vocabulary=ICD10CM" in url_str
        assert "include_invalid=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_map_concepts(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async mapping concepts."""
        respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        result = await async_client.mappings.map(
            source_concepts=[{"concept_id": 201826}],
            target_vocabulary="ICD10CM",
        )

        assert "mappings" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_map_concepts_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async mapping with options."""
        route = respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        await async_client.mappings.map(
            source_concepts=[{"concept_id": 201826}],
            target_vocabulary="ICD10CM",
            mapping_type="direct",
            include_invalid=True,
        )

        assert route.calls[0].request.content
