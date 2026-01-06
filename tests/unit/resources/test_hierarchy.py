"""Tests for the hierarchy resource."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import respx
from httpx import Response

if TYPE_CHECKING:
    import omophub
    from omophub import OMOPHub


class TestHierarchyResource:
    """Tests for the synchronous Hierarchy resource."""

    @respx.mock
    def test_get_ancestors(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting concept ancestors."""
        ancestors_response = {
            "success": True,
            "data": {
                "ancestors": [
                    {"concept_id": 201820, "concept_name": "Diabetes mellitus", "level": 1},
                    {"concept_id": 4000, "concept_name": "Endocrine disorder", "level": 2},
                ],
                "summary": {"total_ancestors": 2, "max_level": 2},
            },
        }
        respx.get(f"{base_url}/concepts/201826/ancestors").mock(
            return_value=Response(200, json=ancestors_response)
        )

        result = sync_client.hierarchy.ancestors(201826)
        assert "ancestors" in result

    @respx.mock
    def test_get_ancestors_with_options(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting ancestors with all options."""
        route = respx.get(f"{base_url}/concepts/201826/ancestors").mock(
            return_value=Response(
                200, json={"success": True, "data": {"ancestors": []}}
            )
        )

        sync_client.hierarchy.ancestors(
            201826,
            vocabulary_ids=["SNOMED"],
            max_levels=5,
            relationship_types=["Is a", "Subsumes"],
            include_paths=True,
            include_distance=True,
            include_invalid=True,
            page=2,
            page_size=50,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "max_levels=5" in url_str
        assert "relationship_types=Is+a%2CSubsumes" in url_str
        assert "include_paths=true" in url_str
        assert "include_distance=true" in url_str
        assert "include_invalid=true" in url_str
        assert "page=2" in url_str
        assert "page_size=50" in url_str

    @respx.mock
    def test_get_descendants(self, sync_client: OMOPHub, base_url: str) -> None:
        """Test getting concept descendants."""
        descendants_response = {
            "success": True,
            "data": {
                "descendants": [
                    {"concept_id": 201826, "concept_name": "Type 2 diabetes mellitus"},
                ],
                "summary": {"total_descendants": 1},
            },
        }
        respx.get(f"{base_url}/concepts/201820/descendants").mock(
            return_value=Response(200, json=descendants_response)
        )

        result = sync_client.hierarchy.descendants(201820)
        assert "descendants" in result

    @respx.mock
    def test_get_descendants_with_options(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test getting descendants with all options."""
        route = respx.get(f"{base_url}/concepts/201820/descendants").mock(
            return_value=Response(
                200, json={"success": True, "data": {"descendants": []}}
            )
        )

        sync_client.hierarchy.descendants(
            201820,
            vocabulary_ids=["SNOMED"],
            max_levels=3,
            relationship_types=["Is a"],
            include_distance=True,
            include_paths=True,
            include_invalid=True,
            domain_ids=["Condition"],
            page=1,
            page_size=100,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "max_levels=3" in url_str
        assert "relationship_types=Is+a" in url_str
        assert "include_distance=true" in url_str
        assert "include_paths=true" in url_str
        assert "include_invalid=true" in url_str
        assert "domain_ids=Condition" in url_str
        assert "page=1" in url_str
        assert "page_size=100" in url_str

    @respx.mock
    def test_get_descendants_max_levels_capped(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test that max_levels is capped at 20."""
        route = respx.get(f"{base_url}/concepts/201820/descendants").mock(
            return_value=Response(
                200, json={"success": True, "data": {"descendants": []}}
            )
        )

        # Request max_levels=50, should be capped to 20
        sync_client.hierarchy.descendants(201820, max_levels=50)

        url_str = str(route.calls[0].request.url)
        assert "max_levels=20" in url_str



class TestAsyncHierarchyResource:
    """Tests for the asynchronous AsyncHierarchy resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_ancestors(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting ancestors."""
        respx.get(f"{base_url}/concepts/201826/ancestors").mock(
            return_value=Response(
                200, json={"success": True, "data": {"ancestors": []}}
            )
        )

        result = await async_client.hierarchy.ancestors(201826)
        assert "ancestors" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_ancestors_with_options(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async ancestors with options."""
        route = respx.get(f"{base_url}/concepts/201826/ancestors").mock(
            return_value=Response(
                200, json={"success": True, "data": {"ancestors": []}}
            )
        )

        await async_client.hierarchy.ancestors(
            201826,
            vocabulary_ids=["SNOMED"],
            max_levels=3,
            relationship_types=["Is a"],
            include_paths=True,
            include_invalid=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "max_levels=3" in url_str
        assert "include_paths=true" in url_str
        assert "relationship_types=Is+a" in url_str
        assert "include_invalid=true" in url_str

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_descendants(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async getting descendants."""
        respx.get(f"{base_url}/concepts/201820/descendants").mock(
            return_value=Response(
                200, json={"success": True, "data": {"descendants": []}}
            )
        )

        result = await async_client.hierarchy.descendants(201820)
        assert "descendants" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_descendants_with_filters(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async descendants with filters."""
        route = respx.get(f"{base_url}/concepts/201820/descendants").mock(
            return_value=Response(
                200, json={"success": True, "data": {"descendants": []}}
            )
        )

        await async_client.hierarchy.descendants(
            201820,
            vocabulary_ids=["SNOMED"],
            max_levels=5,
            domain_ids=["Condition"],
            include_invalid=True,
            include_paths=True,
        )

        url_str = str(route.calls[0].request.url)
        assert "vocabulary_ids=SNOMED" in url_str
        assert "domain_ids=Condition" in url_str
        assert "include_invalid=true" in url_str
        assert "max_levels=5" in url_str
        assert "include_paths=true" in url_str

