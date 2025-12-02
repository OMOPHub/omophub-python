# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/omopHub/omophub-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/omopHub/omophub-python/releases/tag/v0.1.0
