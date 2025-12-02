"""Tests for pagination utilities."""

from __future__ import annotations

import pytest

from omophub._pagination import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PaginationHelper,
    paginate_async,
    paginate_sync,
)


class TestPaginationHelper:
    """Tests for PaginationHelper class."""

    def test_build_query_string_defaults(self) -> None:
        """Test building query string with default values."""
        result = PaginationHelper.build_query_string()
        assert "page=1" in result
        assert f"page_size={DEFAULT_PAGE_SIZE}" in result

    def test_build_query_string_with_params(self) -> None:
        """Test building query string with additional parameters."""
        result = PaginationHelper.build_query_string(
            params={"query": "diabetes", "vocabulary_id": "SNOMED"},
            page=2,
            page_size=50,
        )
        assert "page=2" in result
        assert "page_size=50" in result
        assert "query=diabetes" in result
        assert "vocabulary_id=SNOMED" in result

    def test_build_query_string_with_list_param(self) -> None:
        """Test building query string with list parameter."""
        result = PaginationHelper.build_query_string(
            params={"vocabulary_ids": ["SNOMED", "ICD10CM"]}
        )
        assert "vocabulary_ids=SNOMED%2CICD10CM" in result

    def test_build_query_string_filters_none_values(self) -> None:
        """Test that None values are filtered from params."""
        result = PaginationHelper.build_query_string(
            params={"query": "diabetes", "domain": None}
        )
        assert "query=diabetes" in result
        assert "domain" not in result

    def test_build_query_string_caps_page_size(self) -> None:
        """Test that page size is capped at MAX_PAGE_SIZE."""
        result = PaginationHelper.build_query_string(page_size=5000)
        assert f"page_size={MAX_PAGE_SIZE}" in result

    def test_build_paginated_path_without_existing_query(self) -> None:
        """Test building path without existing query string."""
        result = PaginationHelper.build_paginated_path("/concepts", page=1, page_size=20)
        assert result.startswith("/concepts?")
        assert "page=1" in result

    def test_build_paginated_path_with_existing_query(self) -> None:
        """Test building path with existing query string."""
        result = PaginationHelper.build_paginated_path(
            "/concepts?include=synonyms", page=2, page_size=50
        )
        assert "/concepts?include=synonyms&" in result
        assert "page=2" in result

    def test_has_more_pages_true(self) -> None:
        """Test has_more_pages returns True when has_next is True."""
        meta = {"page": 1, "page_size": 20, "total_pages": 5, "has_next": True}
        assert PaginationHelper.has_more_pages(meta) is True

    def test_has_more_pages_false(self) -> None:
        """Test has_more_pages returns False when has_next is False."""
        meta = {"page": 5, "page_size": 20, "total_pages": 5, "has_next": False}
        assert PaginationHelper.has_more_pages(meta) is False

    def test_has_more_pages_missing_key(self) -> None:
        """Test has_more_pages returns False when has_next is missing."""
        meta = {"page": 1, "page_size": 20}  # type: ignore
        assert PaginationHelper.has_more_pages(meta) is False


class TestPaginateSync:
    """Tests for paginate_sync function."""

    def test_single_page(self) -> None:
        """Test iteration with single page of results."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        meta = {"page": 1, "total_pages": 1, "has_next": False}

        def fetch_page(page: int, page_size: int) -> tuple:
            return items, meta

        result = list(paginate_sync(fetch_page))
        assert result == items

    def test_multiple_pages(self) -> None:
        """Test iteration across multiple pages."""
        pages = {
            1: ([{"id": 1}, {"id": 2}], {"page": 1, "has_next": True}),
            2: ([{"id": 3}, {"id": 4}], {"page": 2, "has_next": True}),
            3: ([{"id": 5}], {"page": 3, "has_next": False}),
        }

        def fetch_page(page: int, page_size: int) -> tuple:
            return pages[page]

        result = list(paginate_sync(fetch_page))
        assert len(result) == 5
        assert result == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]

    def test_empty_result(self) -> None:
        """Test iteration with empty results."""

        def fetch_page(page: int, page_size: int) -> tuple:
            return [], {"page": 1, "total_pages": 0, "has_next": False}

        result = list(paginate_sync(fetch_page))
        assert result == []

    def test_none_meta(self) -> None:
        """Test iteration when meta is None (single page assumed)."""
        items = [{"id": 1}]

        def fetch_page(page: int, page_size: int) -> tuple:
            return items, None

        result = list(paginate_sync(fetch_page))
        assert result == items

    def test_custom_page_size(self) -> None:
        """Test that custom page_size is passed to fetch_page."""
        captured_sizes: list[int] = []

        def fetch_page(page: int, page_size: int) -> tuple:
            captured_sizes.append(page_size)
            return [{"id": 1}], {"has_next": False}

        list(paginate_sync(fetch_page, page_size=100))
        assert captured_sizes == [100]


class TestPaginateAsync:
    """Tests for paginate_async function."""

    @pytest.mark.asyncio
    async def test_single_page(self) -> None:
        """Test async iteration with single page of results."""
        items = [{"id": 1}, {"id": 2}, {"id": 3}]
        meta = {"page": 1, "total_pages": 1, "has_next": False}

        async def fetch_page(page: int, page_size: int) -> tuple:
            return items, meta

        result = [item async for item in paginate_async(fetch_page)]
        assert result == items

    @pytest.mark.asyncio
    async def test_multiple_pages(self) -> None:
        """Test async iteration across multiple pages."""
        pages = {
            1: ([{"id": 1}, {"id": 2}], {"page": 1, "has_next": True}),
            2: ([{"id": 3}, {"id": 4}], {"page": 2, "has_next": True}),
            3: ([{"id": 5}], {"page": 3, "has_next": False}),
        }

        async def fetch_page(page: int, page_size: int) -> tuple:
            return pages[page]

        result = [item async for item in paginate_async(fetch_page)]
        assert len(result) == 5
        assert result == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]

    @pytest.mark.asyncio
    async def test_empty_result(self) -> None:
        """Test async iteration with empty results."""

        async def fetch_page(page: int, page_size: int) -> tuple:
            return [], {"page": 1, "total_pages": 0, "has_next": False}

        result = [item async for item in paginate_async(fetch_page)]
        assert result == []

    @pytest.mark.asyncio
    async def test_none_meta(self) -> None:
        """Test async iteration when meta is None."""
        items = [{"id": 1}]

        async def fetch_page(page: int, page_size: int) -> tuple:
            return items, None

        result = [item async for item in paginate_async(fetch_page)]
        assert result == items

    @pytest.mark.asyncio
    async def test_sync_callable_fallback(self) -> None:
        """Test paginate_async works with sync callables too."""
        items = [{"id": 1}, {"id": 2}]
        meta = {"page": 1, "has_next": False}

        def fetch_page(page: int, page_size: int) -> tuple:
            return items, meta

        result = [item async for item in paginate_async(fetch_page)]
        assert result == items
