# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-04-14

### Added

- **FHIR type interoperability** (`client.fhir.*`): The resolver now
  accepts any Coding-like input via duck typing, so pipelines that
  already parse FHIR with `fhir.resources` or `fhirpy` can pass those
  objects directly - no manual conversion.
  - New `coding=` kwarg on `Fhir.resolve` / `AsyncFhir.resolve`. Accepts
    a plain dict, the `omophub.types.fhir.Coding` TypedDict, or any
    object exposing `.system` / `.code` / `.display` attributes (e.g.
    `fhir.resources.Coding`, `fhirpy` codings).
  - `Fhir.resolve_batch` / `AsyncFhir.resolve_batch` now accept a
    mixed list of dicts and Coding-like objects; each item is
    normalized to the wire format automatically.
  - `Fhir.resolve_codeable_concept` / async counterpart now accept
    either a list of Coding-likes (existing) or a full
    CodeableConcept-like object exposing `.coding` and `.text`
    (new); explicit `text=` kwarg still wins when both are passed.
  - Explicit `system` / `code` kwargs override the corresponding
    fields on a `coding=` input - handy for last-mile overrides.
- **New FHIR type definitions** in `omophub.types.fhir`:
  - `Coding` and `CodeableConcept` lightweight TypedDicts
  - `CodingLike` and `CodeableConceptLike` runtime-checkable
    `Protocol`s for structural matching against external libraries.
- **FHIR client interop helpers** (`omophub.fhir_interop`): Thin
  helpers for configuring an external FHIR client library against
  the OMOPHub FHIR Terminology Service.
  - `get_fhir_server_url(version)` returns the FHIR base URL for
    `"r4"` (default), `"r4b"`, `"r5"`, or `"r6"`.
  - `get_fhirpy_client(api_key, version)` and
    `get_async_fhirpy_client(api_key, version)` return `fhirpy`
    clients pre-wired with the right URL and `Authorization: Bearer`
    header. `fhirpy` is imported lazily, so it is never a required
    dependency; a helpful `ImportError` with install instructions is
    raised only when you actually call the helper.
  - All three helpers are re-exported from the top-level `omophub`
    namespace.
- **`OMOPHub.fhir_server_url` / `AsyncOMOPHub.fhir_server_url`**:
  Convenience read-only property returning the R4 FHIR endpoint for
  drop-in use with external FHIR clients (`httpx`, `fhirpy`,
  `fhir.resources`).
- **Optional extras** in `pyproject.toml`:
  - `pip install omophub[fhirpy]` pulls in `fhirpy>=1.4.0`.
  - `pip install omophub[fhir-resources]` pulls in
    `fhir.resources>=7.0.0`.
  Both are purely optional; duck typing means neither is required
  for core SDK use.

### Changed

- `Fhir.resolve_batch` signature broadened from
  `codings: list[dict[str, str | None]]` to
  `codings: list[CodingInput]` where `CodingInput` is the union of
  dict, `Coding` TypedDict, and `CodingLike` protocol. Existing
  call sites keep working unchanged.
- `Fhir.resolve_codeable_concept` signature broadened from
  `coding: list[dict[str, str]]` to
  `coding: list[CodingInput] | CodeableConceptInput`, accepting
  either the legacy list-of-codings shape or a full
  CodeableConcept-like object.

### Tests

- 16 new unit tests covering `_extract_coding`, `_coding_to_dict`,
  and duck-typed inputs across `resolve`, `resolve_batch`, and
  `resolve_codeable_concept` on the sync client. Explicit-kwargs-win
  precedence is covered.
- New `tests/unit/test_fhir_interop.py` with 10 cases: URL builder
  for all four FHIR versions, `fhirpy` lazy import with stubbed
  success and missing-module failure paths, and the
  `fhir_server_url` property on both sync and async clients.
- 5 new integration tests in `tests/integration/test_fhir.py`
  exercising the new `coding=` kwarg, mixed dict + duck-typed batch
  inputs, CodeableConcept-like object resolution, and the
  `fhir_server_url` property against the live API.

## [1.6.0] - 2026-04-10

### Added

- **FHIR-to-OMOP Concept Resolver** (`client.fhir`): Translate FHIR coded values into OMOP standard concepts, CDM target tables, and optional Phoebe recommendations in a single API call.
  - `resolve()`: Resolve a single FHIR `Coding` (system URI + code) or text-only input via semantic search fallback. Returns the standard concept, target CDM table, domain alignment check, and optional mapping quality signal.
  - `resolve_batch()`: Batch-resolve up to 100 FHIR codings per request with inline per-item error reporting. Failed items do not fail the batch.
  - `resolve_codeable_concept()`: Resolve a FHIR `CodeableConcept` with multiple codings. Automatically picks the best match per OHDSI vocabulary preference (SNOMED > RxNorm > LOINC > CVX > ICD-10). Falls back to the `text` field via semantic search when no coding resolves.
- New TypedDict types for FHIR resolver: `FhirResolveResult`, `FhirResolution`, `FhirBatchResult`, `FhirBatchSummary`, `FhirCodeableConceptResult`, `ResolvedConcept`, `RecommendedConceptOutput`.
- Both sync (`OMOPHub`) and async (`AsyncOMOPHub`) clients support FHIR resolver methods via `client.fhir.*`.

### Changed

- **Extracted shared response parsing** (`_request.py`): The duplicated JSON decode / error-handling / rate-limit-retry logic across `Request._parse_response`, `Request._parse_response_raw`, `AsyncRequest._parse_response`, and `AsyncRequest._parse_response_raw` (4 copies of ~50 lines each) is now a single `_parse_and_raise()` module-level function. All four methods delegate to it, eliminating the risk of divergence bugs.
- **Fixed `paginate_async` signature** (`_pagination.py`): The type hint now correctly declares `Callable[[int, int], Awaitable[tuple[...]]]` instead of `Callable[[int, int], tuple[...]]`, and the runtime `hasattr(__await__)` duck-typing hack has been replaced with a clean `await`.
- **`AsyncSearch.semantic_iter`** now delegates to `paginate_async` instead of manually reimplementing the pagination loop, matching the sync `semantic_iter` which already uses `paginate_sync`.

### Fixed

- Python prerequisite in CONTRIBUTING.md corrected from `3.9+` to `3.10+` (matching `pyproject.toml`).
- `__all__` in `types/__init__.py` sorted per RUF022.

## [1.5.1] - 2026-04-08

### Fixed

- **Rate-limit handling**: HTTP client now respects the `Retry-After` header on `429 Too Many Requests` responses and applies exponential backoff with jitter on retries. Previous versions retried only on `502/503/504` with a fixed `2^attempt * 0.5s` schedule and did not back off on `429` at all, so a client that hit the server's rate limit at high volume could burn through thousands of failed requests in a tight loop. The client now honors `Retry-After`, uses exponential backoff with jitter, respects the configured `max_retries`, and caps backoff at 30 seconds.
- Updated `examples/search_concepts.py` to reflect current API.

## [1.5.0] - 2026-03-26

### Added

- **Bulk lexical search** (`search.bulk_basic()`): Execute up to 50 keyword searches in a single API call. Supports shared defaults for vocabulary, domain, and other filters. Each search is identified by a unique `search_id` for result matching. Maps to `POST /v1/search/bulk`.
- **Bulk semantic search** (`search.bulk_semantic()`): Execute up to 25 natural-language searches using neural embeddings in a single call. Supports per-search similarity thresholds and shared defaults. Includes query enhancement data (abbreviation expansion, misspelling correction). Maps to `POST /v1/search/semantic-bulk`.
- New TypedDict types for bulk search: `BulkSearchInput`, `BulkSearchDefaults`, `BulkSearchResponse`, `BulkSearchResultItem`, `BulkSemanticSearchInput`, `BulkSemanticSearchDefaults`, `BulkSemanticSearchResponse`, `BulkSemanticSearchResultItem`, `QueryEnhancement`.
- Both sync (`OMOPHub`) and async (`AsyncOMOPHub`) clients support bulk search methods.

### Changed

- Updated `__all__` exports to alphabetical order (ruff RUF022 compliance).
- `BulkSearchInput` and `BulkSemanticSearchInput` now use `Required[str]` for `search_id` and `query` fields for proper type checking.

## [1.4.1] - 2026-02-28

### Fixed

- User-Agent header now reports actual SDK version (e.g., `OMOPHub-SDK-Python/1.4.1`) instead of hardcoded `0.1.0`. Version is resolved at runtime via `importlib.metadata`.

## [1.4.0] - 2026-02-23

### Added

- **Semantic search** (`search.semantic()`, `search.semantic_iter()`): Natural language concept search using neural embeddings. Search for clinical intent like "high blood sugar levels" to find diabetes-related concepts. Supports filtering by vocabulary, domain, standard concept, concept class, and minimum similarity threshold. `semantic_iter()` provides automatic pagination.
- **Similarity search** (`search.similar()`): Find concepts similar to a reference concept ID, concept name, or natural language query. Three algorithm options: `'semantic'` (neural embeddings), `'lexical'` (string matching), and `'hybrid'` (combined). Configurable similarity threshold with optional detailed scores and explanations.

## [1.3.1] - 2026-01-24

### Fixed

- Fixed `search.basic_iter()` pagination bug that caused only the first page of results to be returned. The iterator now correctly fetches all pages when iterating through search results.

### Changed

- Added `get_raw()` method to internal request classes for retrieving full API responses with pagination metadata.
- Expanded `search.basic_iter()` method signature to explicitly list all filter parameters instead of using `**kwargs`.

## [1.3.0] - 2026-01-06

### Changes

**Parameter Renames (for API consistency):**
- `search.autocomplete()`: `max_suggestions` → `page_size`
- `concepts.suggest()`: `vocabulary` → `vocabulary_ids`, `domain` → `domain_ids`, `limit` → `page_size`
- `concepts.related()`: `relatedness_types` → `relationship_types`
- `concepts.relationships()`: `relationship_type` → `relationship_ids`
- `relationships.get()`: `relationship_type` → `relationship_ids`, `target_vocabulary` → `vocabulary_ids`
- `hierarchy.ancestors()`: `vocabulary_id` → `vocabulary_ids`, `include_deprecated` → `include_invalid`
- `hierarchy.descendants()`: `vocabulary_id` → `vocabulary_ids`, `include_deprecated` → `include_invalid`

**Simplified APIs (removed parameters):**
- `vocabularies.get()`: Removed `include_stats`, `include_domains` (use `stats()` method instead)
- `vocabularies.domains()`: Removed pagination parameters, now returns all domains
- `domains.list()`: Simplified to single `include_stats` parameter
- `domains.concepts()`: Removed `concept_class_ids`, added `include_invalid`
- `mappings.get()`: Simplified to `target_vocabulary`, `include_invalid`, `vocab_release`
- `relationships.types()`: Removed all filtering parameters

**Default Changes:**
- `vocabularies.list()`: Default `page_size` changed from 100 to 20
- `concepts.batch()`: Default `standard_only` changed from `False` to `True`

### Added

- `vocabularies.domain_stats(vocabulary_id, domain_id)` - Get statistics for a specific domain within a vocabulary
- `vocabularies.concept_classes()` - Get all concept classes
- `hierarchy.get(concept_id)` - Get complete hierarchy (ancestors and descendants) in one call
- `vocab_release` parameter to `concepts.get()`, `concepts.get_by_code()`, `mappings.get()`, `mappings.map()`
- `include_hierarchy` parameter to `concepts.get()` and `concepts.get_by_code()`
- Pagination support to `concepts.suggest()`
- `domain_ids`, `standard_only`, `include_reverse` parameters to `relationships.get()`

## [1.2.0] - 2025-12-09

### Added

- `include_synonyms` and `include_relationships` parameters to `concepts.get_by_code()` method for retrieving concept synonyms and relationships in a single request.

### Changed

- User-Agent header updated to `OMOPHub-SDK-Python/{version}`.

## [0.1.0] - 2025-12-01

### Added

- Initial release of the OMOPHub Python SDK
- Synchronous client (`OMOPHub`) and asynchronous client (`AsyncOMOPHub`)
- Full support for all OMOPHub API endpoints:
  - Concepts: get, get_by_code, batch, suggest, related, relationships
  - Search: basic, advanced, autocomplete
  - Hierarchy: ancestors, descendants, paths
  - Relationships: get, types
  - Mappings: get, map, bulk
  - Vocabularies: list, get, stats, domains, concepts
  - Domains: list, get, concepts
- TypedDict type definitions for all API responses
- Automatic retry with exponential backoff
- Rate limit handling with Retry-After support
- Comprehensive exception hierarchy
- Auto-pagination iterators for search results
- Full type hints and PEP 561 compliance
- HTTP/2 support via httpx

[Unreleased]: https://github.com/omopHub/omophub-python/compare/v1.6.0...HEAD
[1.6.0]: https://github.com/omopHub/omophub-python/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/omopHub/omophub-python/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/omopHub/omophub-python/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/omopHub/omophub-python/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/omopHub/omophub-python/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/omopHub/omophub-python/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/omopHub/omophub-python/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/omopHub/omophub-python/compare/v0.1.0...v1.2.0
[0.1.0]: https://github.com/omopHub/omophub-python/releases/tag/v0.1.0
