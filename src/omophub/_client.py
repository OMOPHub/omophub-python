"""Main client classes for the OMOPHub SDK."""

from __future__ import annotations

from typing import Any

from ._config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)
from ._config import (
    api_key as default_api_key,
)
from ._exceptions import AuthenticationError
from ._http import AsyncHTTPClientImpl, SyncHTTPClient
from ._request import AsyncRequest, Request
from .resources.concepts import AsyncConcepts, Concepts
from .resources.domains import AsyncDomains, Domains
from .resources.hierarchy import AsyncHierarchy, Hierarchy
from .resources.mappings import AsyncMappings, Mappings
from .resources.relationships import AsyncRelationships, Relationships
from .resources.search import AsyncSearch, Search
from .resources.vocabularies import AsyncVocabularies, Vocabularies


class OMOPHub:
    """Synchronous OMOPHub API client.

    Example:
        >>> import omophub
        >>> client = omophub.OMOPHub(api_key="oh_xxxxxxxxx")
        >>> concept = client.concepts.get(201826)
        >>> print(concept["concept_name"])
        "Type 2 diabetes mellitus"

    Or using the context manager:
        >>> with omophub.OMOPHub(api_key="oh_xxx") as client:
        ...     results = client.search.basic("diabetes")
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        vocab_version: str | None = None,
    ) -> None:
        """Initialize the OMOPHub client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                     OMOPHUB_API_KEY environment variable or module-level omophub.api_key.
            base_url: Base URL for the API. Defaults to https://api.omophub.com/v1
            timeout: Request timeout in seconds. Defaults to 30.
            max_retries: Maximum retry attempts for failed requests. Defaults to 3.
            vocab_version: Optional vocabulary version (e.g., "2025.1").
                          If not specified, uses the latest version.

        Raises:
            AuthenticationError: If no API key is provided.
        """
        self._api_key = api_key or default_api_key
        if not self._api_key:
            raise AuthenticationError(
                "API key is required. Provide it as an argument, set the "
                "OMOPHUB_API_KEY environment variable, or set omophub.api_key.",
                status_code=401,
            )

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._vocab_version = vocab_version

        # Initialize HTTP client
        self._http_client = SyncHTTPClient(
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize request handler
        self._request: Request[Any] = Request(
            http_client=self._http_client,
            base_url=self._base_url,
            api_key=self._api_key,
            vocab_version=self._vocab_version,
        )

        # Initialize resources
        self._concepts: Concepts | None = None
        self._search: Search | None = None
        self._hierarchy: Hierarchy | None = None
        self._relationships: Relationships | None = None
        self._mappings: Mappings | None = None
        self._vocabularies: Vocabularies | None = None
        self._domains: Domains | None = None

    @property
    def concepts(self) -> Concepts:
        """Access the concepts resource."""
        if self._concepts is None:
            self._concepts = Concepts(self._request)
        return self._concepts

    @property
    def search(self) -> Search:
        """Access the search resource."""
        if self._search is None:
            self._search = Search(self._request)
        return self._search

    @property
    def hierarchy(self) -> Hierarchy:
        """Access the hierarchy resource."""
        if self._hierarchy is None:
            self._hierarchy = Hierarchy(self._request)
        return self._hierarchy

    @property
    def relationships(self) -> Relationships:
        """Access the relationships resource."""
        if self._relationships is None:
            self._relationships = Relationships(self._request)
        return self._relationships

    @property
    def mappings(self) -> Mappings:
        """Access the mappings resource."""
        if self._mappings is None:
            self._mappings = Mappings(self._request)
        return self._mappings

    @property
    def vocabularies(self) -> Vocabularies:
        """Access the vocabularies resource."""
        if self._vocabularies is None:
            self._vocabularies = Vocabularies(self._request)
        return self._vocabularies

    @property
    def domains(self) -> Domains:
        """Access the domains resource."""
        if self._domains is None:
            self._domains = Domains(self._request)
        return self._domains

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._http_client.close()

    def __enter__(self) -> OMOPHub:
        """Enter context manager."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager and close client."""
        self.close()


class AsyncOMOPHub:
    """Asynchronous OMOPHub API client.

    Example:
        >>> import omophub
        >>> async with omophub.AsyncOMOPHub(api_key="oh_xxx") as client:
        ...     concept = await client.concepts.get(201826)
        ...     print(concept["concept_name"])
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        vocab_version: str | None = None,
    ) -> None:
        """Initialize the async OMOPHub client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                     OMOPHUB_API_KEY environment variable or module-level omophub.api_key.
            base_url: Base URL for the API. Defaults to https://api.omophub.com/v1
            timeout: Request timeout in seconds. Defaults to 30.
            max_retries: Maximum retry attempts for failed requests. Defaults to 3.
            vocab_version: Optional vocabulary version (e.g., "2025.1").
                          If not specified, uses the latest version.

        Raises:
            AuthenticationError: If no API key is provided.
        """
        self._api_key = api_key or default_api_key
        if not self._api_key:
            raise AuthenticationError(
                "API key is required. Provide it as an argument, set the "
                "OMOPHUB_API_KEY environment variable, or set omophub.api_key.",
                status_code=401,
            )

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._vocab_version = vocab_version

        # Initialize HTTP client
        self._http_client = AsyncHTTPClientImpl(
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize request handler
        self._request: AsyncRequest[Any] = AsyncRequest(
            http_client=self._http_client,
            base_url=self._base_url,
            api_key=self._api_key,
            vocab_version=self._vocab_version,
        )

        # Initialize resources
        self._concepts: AsyncConcepts | None = None
        self._search: AsyncSearch | None = None
        self._hierarchy: AsyncHierarchy | None = None
        self._relationships: AsyncRelationships | None = None
        self._mappings: AsyncMappings | None = None
        self._vocabularies: AsyncVocabularies | None = None
        self._domains: AsyncDomains | None = None

    @property
    def concepts(self) -> AsyncConcepts:
        """Access the concepts resource."""
        if self._concepts is None:
            self._concepts = AsyncConcepts(self._request)
        return self._concepts

    @property
    def search(self) -> AsyncSearch:
        """Access the search resource."""
        if self._search is None:
            self._search = AsyncSearch(self._request)
        return self._search

    @property
    def hierarchy(self) -> AsyncHierarchy:
        """Access the hierarchy resource."""
        if self._hierarchy is None:
            self._hierarchy = AsyncHierarchy(self._request)
        return self._hierarchy

    @property
    def relationships(self) -> AsyncRelationships:
        """Access the relationships resource."""
        if self._relationships is None:
            self._relationships = AsyncRelationships(self._request)
        return self._relationships

    @property
    def mappings(self) -> AsyncMappings:
        """Access the mappings resource."""
        if self._mappings is None:
            self._mappings = AsyncMappings(self._request)
        return self._mappings

    @property
    def vocabularies(self) -> AsyncVocabularies:
        """Access the vocabularies resource."""
        if self._vocabularies is None:
            self._vocabularies = AsyncVocabularies(self._request)
        return self._vocabularies

    @property
    def domains(self) -> AsyncDomains:
        """Access the domains resource."""
        if self._domains is None:
            self._domains = AsyncDomains(self._request)
        return self._domains

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._http_client.close()

    async def __aenter__(self) -> AsyncOMOPHub:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager and close client."""
        await self.close()
