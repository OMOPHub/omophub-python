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
    def test_get_mappings_sends_relationship_ids(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Value-as-Concept is unreachable without this parameter.

        The server defaults to `Maps to` alone, so a composite concept returns
        only half its decomposition unless `Maps to value` is asked for.
        """
        route = respx.get(f"{base_url}/concepts/4167462/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        sync_client.mappings.get(4167462)
        assert "relationship_ids" not in str(route.calls[0].request.url)

        sync_client.mappings.get(4167462, relationship_ids=["Maps to", "Maps to value"])
        assert route.calls[1].request.url.params["relationship_ids"] == (
            "Maps to,Maps to value"
        )

        # A bare string is passed through unjoined, matching concepts.relationships().
        sync_client.mappings.get(4167462, relationship_ids="Maps to value")
        assert route.calls[2].request.url.params["relationship_ids"] == "Maps to value"

    @respx.mock
    def test_get_iter_forwards_relationship_ids(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """The filter has to survive the pagination helper too."""
        route = respx.get(f"{base_url}/concepts/4167462/mappings").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": []},
                    "meta": {
                        "pagination": {
                            "page": 1,
                            "page_size": 100,
                            "total_items": 0,
                            "total_pages": 0,
                            "has_next": False,
                            "has_previous": False,
                        }
                    },
                },
            )
        )

        list(
            sync_client.mappings.get_iter(
                4167462, relationship_ids=["Maps to", "Maps to value"]
            )
        )
        assert route.calls[0].request.url.params["relationship_ids"] == (
            "Maps to,Maps to value"
        )

    @respx.mock
    def test_get_mappings_include_invalid_is_tri_state(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """False must reach the wire, not be dropped as falsy.

        This endpoint defaults to *including* deprecated mappings, so omitting
        the parameter and sending ``false`` mean different things. Sending
        nothing for ``include_invalid=False`` silently returned the rows the
        caller asked to exclude.
        """
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        sync_client.mappings.get(201826)
        assert "include_invalid" not in str(route.calls[0].request.url)

        sync_client.mappings.get(201826, include_invalid=False)
        assert "include_invalid=false" in str(route.calls[1].request.url)

        sync_client.mappings.get(201826, include_invalid=True)
        assert "include_invalid=true" in str(route.calls[2].request.url)

    @respx.mock
    def test_get_iter_forwards_include_invalid_false(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """The same tri-state has to survive the pagination helper."""
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": []},
                    "meta": {
                        "pagination": {
                            "page": 1,
                            "page_size": 100,
                            "total_items": 0,
                            "total_pages": 0,
                            "has_next": False,
                            "has_previous": False,
                        }
                    },
                },
            )
        )

        list(sync_client.mappings.get_iter(201826, include_invalid=False))
        assert "include_invalid=false" in str(route.calls[0].request.url)

    @respx.mock
    def test_get_mappings_sends_pagination(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """page/page_size reach the wire, including their defaults."""
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        sync_client.mappings.get(201826)
        default_url = str(route.calls[0].request.url)
        assert "page=1" in default_url
        assert "page_size=100" in default_url

        sync_client.mappings.get(201826, page=3, page_size=200)
        paged_url = str(route.calls[1].request.url)
        assert "page=3" in paged_url
        assert "page_size=200" in paged_url

    @respx.mock
    def test_get_iter_walks_every_page(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """get_iter follows has_next instead of stopping at the first page."""
        pages = [
            Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": [{"target_concept_id": 1}]},
                    "meta": {"pagination": {"has_next": True, "total_items": 2}},
                },
            ),
            Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": [{"target_concept_id": 2}]},
                    "meta": {"pagination": {"has_next": False, "total_items": 2}},
                },
            ),
        ]
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            side_effect=pages
        )

        result = list(sync_client.mappings.get_iter(201826, page_size=1))

        assert [m["target_concept_id"] for m in result] == [1, 2]
        assert len(route.calls) == 2
        assert "page=2" in str(route.calls[1].request.url)

    @respx.mock
    def test_get_iter_stops_without_pagination_meta(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """A response with no pagination meta terminates rather than looping."""
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            return_value=Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": [{"target_concept_id": 1}]},
                },
            )
        )

        result = list(sync_client.mappings.get_iter(201826))

        assert len(result) == 1
        assert len(route.calls) == 1

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
            target_vocabulary="ICD10CM",
            source_concepts=[201826],
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
            target_vocabulary="ICD10CM",
            source_concepts=[201826, 4329847],
            mapping_type="equivalent",
            include_invalid=True,
        )

        # Verify POST body
        assert route.calls[0].request.content

    @respx.mock
    def test_map_concepts_with_source_codes(
        self, sync_client: OMOPHub, base_url: str
    ) -> None:
        """Test mapping concepts using source_codes parameter."""
        import json

        map_response = {
            "success": True,
            "data": {
                "mappings": [
                    {
                        "source_concept_id": 4306040,
                        "source_concept_name": "Acetaminophen",
                        "target_concept_id": 1125315,
                        "target_vocabulary_id": "RxNorm",
                    }
                ],
            },
        }
        route = respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json=map_response)
        )

        result = sync_client.mappings.map(
            target_vocabulary="RxNorm",
            source_codes=[
                {"vocabulary_id": "SNOMED", "concept_code": "387517004"},
                {"vocabulary_id": "SNOMED", "concept_code": "108774000"},
            ],
        )

        assert "mappings" in result
        # Verify request body contains source_codes
        body = json.loads(route.calls[0].request.content)
        assert "source_codes" in body
        assert len(body["source_codes"]) == 2
        assert body["source_codes"][0]["vocabulary_id"] == "SNOMED"

    def test_map_concepts_requires_source(self, sync_client: OMOPHub) -> None:
        """Test that map() raises error when neither source_concepts nor source_codes provided."""
        with pytest.raises(
            ValueError, match="Either source_concepts or source_codes is required"
        ):
            sync_client.mappings.map(target_vocabulary="ICD10CM")

    def test_map_concepts_rejects_both_sources(self, sync_client: OMOPHub) -> None:
        """Test that map() raises error when both source_concepts and source_codes provided."""
        with pytest.raises(
            ValueError, match="Cannot use both source_concepts and source_codes"
        ):
            sync_client.mappings.map(
                target_vocabulary="ICD10CM",
                source_concepts=[201826],
                source_codes=[{"vocabulary_id": "SNOMED", "concept_code": "44054006"}],
            )


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
    async def test_async_get_iter_walks_every_page(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Async get_iter follows has_next across pages."""
        pages = [
            Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": [{"target_concept_id": 1}]},
                    "meta": {"pagination": {"has_next": True, "total_items": 2}},
                },
            ),
            Response(
                200,
                json={
                    "success": True,
                    "data": {"mappings": [{"target_concept_id": 2}]},
                    "meta": {"pagination": {"has_next": False, "total_items": 2}},
                },
            ),
        ]
        route = respx.get(f"{base_url}/concepts/201826/mappings").mock(
            side_effect=pages
        )

        result = [m async for m in async_client.mappings.get_iter(201826, page_size=1)]

        assert [m["target_concept_id"] for m in result] == [1, 2]
        assert len(route.calls) == 2
        assert "page=2" in str(route.calls[1].request.url)

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
            target_vocabulary="ICD10CM",
            source_concepts=[201826],
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
            target_vocabulary="ICD10CM",
            source_concepts=[201826],
            mapping_type="direct",
            include_invalid=True,
        )

        assert route.calls[0].request.content

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_map_concepts_with_source_codes(
        self, async_client: omophub.AsyncOMOPHub, base_url: str
    ) -> None:
        """Test async mapping concepts using source_codes."""
        import json

        route = respx.post(f"{base_url}/concepts/map").mock(
            return_value=Response(200, json={"success": True, "data": {"mappings": []}})
        )

        result = await async_client.mappings.map(
            target_vocabulary="RxNorm",
            source_codes=[
                {"vocabulary_id": "SNOMED", "concept_code": "387517004"},
            ],
        )

        assert "mappings" in result
        body = json.loads(route.calls[0].request.content)
        assert "source_codes" in body

    @pytest.mark.asyncio
    async def test_async_map_requires_source(
        self, async_client: omophub.AsyncOMOPHub
    ) -> None:
        """Test async map() raises error without sources."""
        with pytest.raises(
            ValueError, match="Either source_concepts or source_codes is required"
        ):
            await async_client.mappings.map(target_vocabulary="ICD10CM")

    @pytest.mark.asyncio
    async def test_async_map_rejects_both_sources(
        self, async_client: omophub.AsyncOMOPHub
    ) -> None:
        """Test async map() raises error with both sources."""
        with pytest.raises(
            ValueError, match="Cannot use both source_concepts and source_codes"
        ):
            await async_client.mappings.map(
                target_vocabulary="ICD10CM",
                source_concepts=[201826],
                source_codes=[{"vocabulary_id": "SNOMED", "concept_code": "44054006"}],
            )
