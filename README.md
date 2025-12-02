# OMOPHub Python SDK

[![PyPI version](https://badge.fury.io/py/omophub.svg)](https://badge.fury.io/py/omophub)
[![Python Versions](https://img.shields.io/pypi/pyversions/omophub.svg)](https://pypi.org/project/omophub/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [OMOPHub](https://omophub.com) - a medical vocabulary API providing access to OHDSI ATHENA standardized vocabularies including SNOMED CT, ICD-10, RxNorm, LOINC, and 90+ other medical terminologies.

## Installation

```bash
pip install omophub
```

## Quick Start

```python
import omophub

# Initialize the client
client = omophub.OMOPHub(api_key="oh_xxxxxxxxx")

# Get a concept by ID
concept = client.concepts.get(201826)
print(concept["concept_name"])  # "Type 2 diabetes mellitus"

# Search for concepts
results = client.search.basic("diabetes", vocabulary_ids=["SNOMED", "ICD10CM"])
for concept in results["concepts"]:
    print(f"{concept['concept_id']}: {concept['concept_name']}")

# Get concept ancestors
ancestors = client.hierarchy.ancestors(201826, max_levels=3)

# Map concepts between vocabularies
mappings = client.mappings.get(201826, target_vocabularies=["ICD10CM"])
```

## Async Usage

```python
import omophub
import asyncio

async def main():
    async with omophub.AsyncOMOPHub(api_key="oh_xxx") as client:
        concept = await client.concepts.get(201826)
        print(concept["concept_name"])

asyncio.run(main())
```

## Configuration

### API Key

Set your API key in one of three ways:

```python
# 1. Pass directly to client
client = omophub.OMOPHub(api_key="oh_xxxxxxxxx")

# 2. Set environment variable
# export OMOPHUB_API_KEY=oh_xxxxxxxxx
client = omophub.OMOPHub()

# 3. Set module-level variable
import omophub
omophub.api_key = "oh_xxxxxxxxx"
client = omophub.OMOPHub()
```

Get your API key from the [OMOPHub Dashboard](https://dashboard.omophub.com/api-keys).

### Additional Options

```python
client = omophub.OMOPHub(
    api_key="oh_xxx",
    base_url="https://api.omophub.com/v1",  # API base URL
    timeout=30.0,                            # Request timeout in seconds
    max_retries=3,                           # Retry attempts for failed requests
    vocab_version="2025.2",                  # Specific vocabulary version
)
```

## Resources

### Concepts

```python
# Get concept by ID
concept = client.concepts.get(201826)

# Get concept by vocabulary code
concept = client.concepts.get_by_code("SNOMED", "73211009")

# Batch get concepts
result = client.concepts.batch([201826, 4329847, 73211009])

# Get autocomplete suggestions
suggestions = client.concepts.suggest("diab", vocabulary="SNOMED", limit=10)

# Get related concepts
related = client.concepts.related(201826, relatedness_types=["hierarchical", "semantic"])

# Get concept relationships
relationships = client.concepts.relationships(201826)
```

### Search

```python
# Basic search
results = client.search.basic(
    "heart attack",
    vocabulary_ids=["SNOMED"],
    domain_ids=["Condition"],
    page=1,
    page_size=20,
)

# Advanced search with facets
results = client.search.advanced(
    "myocardial infarction",
    vocabularies=["SNOMED", "ICD10CM"],
    standard_concepts_only=True,
)

# Semantic search
results = client.search.semantic("chest pain with shortness of breath")

# Fuzzy search (typo-tolerant)
results = client.search.fuzzy("diabetis")  # finds "diabetes"

# Auto-pagination iterator
for concept in client.search.basic_iter("diabetes", page_size=100):
    print(concept["concept_name"])
```

### Hierarchy

```python
# Get ancestors
ancestors = client.hierarchy.ancestors(
    201826,
    max_levels=5,
    relationship_types=["Is a"],
)

# Get descendants
descendants = client.hierarchy.descendants(
    201826,
    max_levels=3,
    standard_only=True,
)
```

### Mappings

```python
# Get mappings for a concept
mappings = client.mappings.get(
    201826,
    target_vocabularies=["ICD10CM", "Read"],
    include_mapping_quality=True,
)

# Map concepts to target vocabulary
result = client.mappings.map(
    source_concepts=[201826, 4329847],
    target_vocabulary="ICD10CM",
)
```

### Vocabularies

```python
# List all vocabularies
vocabularies = client.vocabularies.list(include_stats=True)

# Get vocabulary details
snomed = client.vocabularies.get("SNOMED", include_domains=True)

# Get vocabulary statistics
stats = client.vocabularies.stats("SNOMED")
```

### Domains

```python
# List all domains
domains = client.domains.list(include_statistics=True)

# Get domain details
condition = client.domains.get("Condition")

# Get concepts in a domain
concepts = client.domains.concepts("Drug", standard_only=True)
```

## Error Handling

```python
import omophub

try:
    client = omophub.OMOPHub(api_key="oh_xxx")
    concept = client.concepts.get(999999999)
except omophub.NotFoundError as e:
    print(f"Concept not found: {e.message}")
except omophub.AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
except omophub.RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except omophub.ValidationError as e:
    print(f"Invalid request: {e.message}")
except omophub.APIError as e:
    print(f"API error {e.status_code}: {e.message}")
except omophub.OMOPHubError as e:
    print(f"SDK error: {e.message}")
```

## Type Hints

The SDK is fully typed with TypedDict definitions for all API responses:

```python
from omophub import OMOPHub, Concept

client = OMOPHub(api_key="oh_xxx")
concept: Concept = client.concepts.get(201826)

# IDE autocomplete works for all fields
print(concept["concept_id"])
print(concept["concept_name"])
print(concept["vocabulary_id"])
```

## Documentation

- [Full Documentation](https://docs.omophub.com/sdks/python/overview)
- [API Reference](https://docs.omophub.com/api-reference)
- [Examples](https://github.com/omopHub/omophub-python/tree/main/examples)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- [GitHub Issues](https://github.com/omopHub/omophub-python/issues)
- [Documentation](https://docs.omophub.com)
