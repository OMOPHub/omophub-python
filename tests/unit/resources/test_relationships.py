"""Tests for the relationships resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestRelationshipsResource:
    """Tests for the synchronous Relationships resource."""

    @respx.mock
    def test_get_relationships(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting relationships for a concept."""
        relationships_response = {
            "success": True,
            "data": {
                "relationships": [
                    {
                        "relationship_id": "Is a",
                        "concept_id_1": 201826,
                        "concept_id_2": 201820,
                        "relationship_name": "Is a",
                    }
                ],
                "summary": {"total_relationships": 1},
            },
        }
        respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(200, json=relationships_response)
        )

        result = sync_client.relationships.get(201826)
        assert "relationships" in result

    @respx.mock
    def test_get_relationships_with_filters(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting relationships with filter options."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        sync_client.relationships.get(
            201826,
            relationship_type="Is a",
            target_vocabulary="SNOMED",
            include_invalid=True,
            page=2,
            page_size=100,
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_type=Is+a" in url_str
        assert "target_vocabulary=SNOMED" in url_str
        assert "include_invalid=true" in url_str
        assert "page=2" in url_str
        assert "page_size=100" in url_str

    @respx.mock
    def test_get_relationship_types(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting available relationship types."""
        types_response = {
            "success": True,
            "data": {
                "relationship_types": [
                    {"relationship_id": "Is a", "relationship_name": "Is a"},
                    {"relationship_id": "Maps to", "relationship_name": "Maps to"},
                ],
                "summary": {"total_types": 2},
            },
        }
        respx.get(f"{base_url}/relationships/types").mock(
            return_value=Response(200, json=types_response)
        )

        result = sync_client.relationships.types()
        assert "relationship_types" in result

    @respx.mock
    def test_get_relationship_types_with_pagination(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting relationship types with pagination options."""
        route = respx.get(f"{base_url}/relationships/types").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationship_types": []}}
            )
        )

        sync_client.relationships.types(page=2, page_size=50)

        url_str = str(route.calls[0].request.url)
        assert "page=2" in url_str
        assert "page_size=50" in url_str


class TestAsyncRelationshipsResource:
    """Tests for the asynchronous AsyncRelationships resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationships(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting relationships."""
        respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        result = await async_client.relationships.get(201826)
        assert "relationships" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationships_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async relationships with filter options."""
        route = respx.get(f"{base_url}/concepts/201826/relationships").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationships": []}}
            )
        )

        await async_client.relationships.get(
            201826,
            relationship_type="Maps to",
            target_vocabulary="ICD10CM",
            include_invalid=True,
            page=1,
            page_size=200,
        )

        url_str = str(route.calls[0].request.url)
        assert "relationship_type=Maps+to" in url_str
        assert "target_vocabulary=ICD10CM" in url_str
        assert "include_invalid=true" in url_str
        assert "page=1" in url_str
        assert "page_size=200" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationship_types(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting relationship types."""
        respx.get(f"{base_url}/relationships/types").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationship_types": []}}
            )
        )

        result = await async_client.relationships.types()
        assert "relationship_types" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_relationship_types_with_pagination(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async relationship types with pagination options."""
        route = respx.get(f"{base_url}/relationships/types").mock(
            return_value=Response(
                200, json={"success": True, "data": {"relationship_types": []}}
            )
        )

        await async_client.relationships.types(page=3, page_size=25)

        url_str = str(route.calls[0].request.url)
        assert "page=3" in url_str
        assert "page_size=25" in url_str
