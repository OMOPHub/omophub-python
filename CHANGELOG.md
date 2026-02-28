# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/omopHub/omophub-python/compare/v1.4.1...HEAD
[1.4.1]: https://github.com/omopHub/omophub-python/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/omopHub/omophub-python/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/omopHub/omophub-python/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/omopHub/omophub-python/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/omopHub/omophub-python/compare/v0.1.0...v1.2.0
[0.1.0]: https://github.com/omopHub/omophub-python/releases/tag/v0.1.0
