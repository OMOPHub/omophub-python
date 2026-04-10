# OMOPHub Python SDK

**Query millions standardized medical concepts via simple Python API**

Access SNOMED CT, ICD-10, RxNorm, LOINC, and 90+ OHDSI ATHENA vocabularies without downloading, installing, or maintaining local databases.

[![PyPI version](https://badge.fury.io/py/omophub.svg)](https://pypi.org/project/omophub/)
[![Python Versions](https://img.shields.io/pypi/pyversions/omophub.svg)](https://pypi.org/project/omophub/)
[![Codecov](https://codecov.io/gh/omopHub/omophub-python/branch/main/graph/badge.svg)](https://app.codecov.io/gh/omopHub/omophub-python?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Downloads](https://img.shields.io/pypi/dm/omophub)

**[Documentation](https://docs.omophub.com/sdks/python/overview)** ·
**[API Reference](https://docs.omophub.com/api-reference)** ·
**[Examples](https://github.com/omopHub/omophub-python/tree/main/examples)**

---

## Why OMOPHub?

Working with OHDSI ATHENA vocabularies traditionally requires downloading multi-gigabyte files, setting up a database instance, and writing complex SQL queries. **OMOPHub eliminates this friction.**

| Traditional Approach | With OMOPHub |
|---------------------|--------------|
| Download 5GB+ ATHENA vocabulary files | `pip install omophub` |
| Set up and maintain database | One API call |
| Write complex SQL with multiple JOINs | Simple Python methods |
| Manually update vocabularies quarterly | Always current data |
| Local infrastructure required | Works anywhere Python runs |

## Installation

```bash
pip install omophub
```

## Quick Start

```python
from omophub import OMOPHub

# Initialize client (uses OMOPHUB_API_KEY env variable, or pass api_key="...")
client = OMOPHub()

# Get a concept by ID
concept = client.concepts.get(201826)
print(concept["concept_name"])  # "Type 2 diabetes mellitus"

# Search for concepts across vocabularies
results = client.search.basic("metformin", vocabulary_ids=["RxNorm"], domain_ids=["Drug"])
for c in results["concepts"]:
    print(f"{c['concept_id']}: {c['concept_name']}")

# Map ICD-10 code to SNOMED
mappings = client.mappings.get_by_code("ICD10CM", "E11.9", target_vocabulary="SNOMED")

# Navigate concept hierarchy
ancestors = client.hierarchy.ancestors(201826, max_levels=3)
```

## FHIR-to-OMOP Resolution

Resolve FHIR coded values to OMOP standard concepts in one call:

```python
# Single FHIR Coding → OMOP concept + CDM target table
result = client.fhir.resolve(
    system="http://snomed.info/sct",
    code="44054006",
    resource_type="Condition",
)
print(result["resolution"]["target_table"])  # "condition_occurrence"
print(result["resolution"]["mapping_type"])  # "direct"

# ICD-10-CM → traverses "Maps to" automatically
result = client.fhir.resolve(
    system="http://hl7.org/fhir/sid/icd-10-cm",
    code="E11.9",
)
print(result["resolution"]["standard_concept"]["vocabulary_id"])  # "SNOMED"

# Batch resolve up to 100 codings
batch = client.fhir.resolve_batch([
    {"system": "http://snomed.info/sct", "code": "44054006"},
    {"system": "http://loinc.org", "code": "2339-0"},
    {"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "197696"},
])
print(f"Resolved {batch['summary']['resolved']}/{batch['summary']['total']}")

# CodeableConcept with vocabulary preference (SNOMED wins over ICD-10)
result = client.fhir.resolve_codeable_concept(
    coding=[
        {"system": "http://snomed.info/sct", "code": "44054006"},
        {"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "E11.9"},
    ],
    resource_type="Condition",
)
print(result["best_match"]["resolution"]["source_concept"]["vocabulary_id"])  # "SNOMED"
```

## Semantic Search

Use natural language queries to find concepts using neural embeddings:

```python
# Natural language search - understands clinical intent
results = client.search.semantic("high blood sugar levels")
for r in results["results"]:
    print(f"{r['concept_name']} (similarity: {r['similarity_score']:.2f})")

# Filter by vocabulary and set minimum similarity threshold
results = client.search.semantic(
    "heart attack",
    vocabulary_ids=["SNOMED"],
    domain_ids=["Condition"],
    threshold=0.5
)

# Iterate through all results with auto-pagination
for result in client.search.semantic_iter("chronic kidney disease", page_size=50):
    print(f"{result['concept_id']}: {result['concept_name']}")
```

### Bulk Search

Search for multiple terms in a single API call — much faster than individual requests:

```python
# Bulk lexical search (up to 50 queries)
results = client.search.bulk_basic([
    {"search_id": "q1", "query": "diabetes mellitus"},
    {"search_id": "q2", "query": "hypertension"},
    {"search_id": "q3", "query": "aspirin"},
], defaults={"vocabulary_ids": ["SNOMED"], "page_size": 5})

for item in results["results"]:
    print(f"{item['search_id']}: {len(item['results'])} results")

# Bulk semantic search (up to 25 queries)
results = client.search.bulk_semantic([
    {"search_id": "s1", "query": "heart failure treatment options"},
    {"search_id": "s2", "query": "type 2 diabetes medication"},
], defaults={"threshold": 0.5, "page_size": 10})
```

### Similarity Search

Find concepts similar to a known concept or natural language query:

```python
# Find concepts similar to a known concept
results = client.search.similar(concept_id=201826, algorithm="hybrid")
for r in results["results"]:
    print(f"{r['concept_name']} (score: {r['similarity_score']:.2f})")

# Find similar concepts using a natural language query
results = client.search.similar(
    query="medications for high blood pressure",
    algorithm="semantic",
    similarity_threshold=0.6,
    vocabulary_ids=["RxNorm"],
    include_scores=True,
)
```

## Async Support

```python
import asyncio
from omophub import AsyncOMOPHub

async def main():
    async with AsyncOMOPHub() as client:
        concept = await client.concepts.get(201826)
        print(concept["concept_name"])

asyncio.run(main())
```

## Use Cases

### ETL & Data Pipelines

Validate and map clinical codes during OMOP CDM transformations:

```python
# Validate that a source code exists and find its standard equivalent
def validate_and_map(source_vocab, source_code):
    concept = client.concepts.get_by_code(source_vocab, source_code)
    if concept["standard_concept"] != "S":
        mappings = client.mappings.get(concept["concept_id"],
                                        target_vocabulary="SNOMED")
        return mappings["mappings"][0]["target_concept_id"]
    return concept["concept_id"]
```

### Data Quality Checks

Verify codes exist and are valid standard concepts:

```python
# Check if all your condition codes are valid
condition_codes = ["E11.9", "I10", "J44.9"]  # ICD-10 codes
for code in condition_codes:
    try:
        concept = client.concepts.get_by_code("ICD10CM", code)
        print(f"OK {code}: {concept['concept_name']}")
    except omophub.NotFoundError:
        print(f"ERROR {code}: Invalid code!")
```

### Phenotype Development

Explore hierarchies to build comprehensive concept sets:

```python
# Get all descendants of "Type 2 diabetes mellitus" for phenotype
descendants = client.hierarchy.descendants(201826, max_levels=5)
concept_set = [d["concept_id"] for d in descendants["concepts"]]
print(f"Found {len(concept_set)} concepts for T2DM phenotype")
```

### Clinical Applications

Build terminology lookups into healthcare applications:

```python
# Autocomplete for clinical coding interface
suggestions = client.concepts.suggest("diab", vocabulary_ids=["SNOMED"], page_size=10)
# Returns: ["Diabetes mellitus", "Diabetic nephropathy", "Diabetic retinopathy", ...]
```

## API Resources

| Resource | Description | Key Methods |
|----------|-------------|-------------|
| `concepts` | Concept lookup and batch operations | `get()`, `get_by_code()`, `batch()`, `suggest()` |
| `search` | Full-text and semantic search | `basic()`, `advanced()`, `semantic()`, `similar()`, `bulk_basic()`, `bulk_semantic()` |
| `hierarchy` | Navigate concept relationships | `ancestors()`, `descendants()` |
| `mappings` | Cross-vocabulary mappings | `get()`, `map()` |
| `vocabularies` | Vocabulary metadata | `list()`, `get()`, `stats()` |
| `domains` | Domain information | `list()`, `get()`, `concepts()` |
| `fhir` | FHIR-to-OMOP resolution | `resolve()`, `resolve_batch()`, `resolve_codeable_concept()` |

## Configuration

```python
client = OMOPHub(
    api_key="oh_xxx",                        # Or set OMOPHUB_API_KEY env var
    base_url="https://api.omophub.com/v1",   # API endpoint
    timeout=30.0,                             # Request timeout (seconds)
    max_retries=3,                            # Retry attempts
    vocab_version="2025.2",                   # Specific vocabulary version
)
```

## Error Handling

```python
import omophub

try:
    concept = client.concepts.get(999999999)
except omophub.NotFoundError as e:
    print(f"Concept not found: {e.message}")
except omophub.AuthenticationError as e:
    print(f"Check your API key: {e.message}")
except omophub.RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except omophub.APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Type Safety

The SDK is fully typed with TypedDict definitions for IDE autocomplete:

```python
from omophub import OMOPHub, Concept

client = OMOPHub()
concept: Concept = client.concepts.get(201826)

# IDE autocomplete works for all fields
concept["concept_id"]      # int
concept["concept_name"]    # str
concept["vocabulary_id"]   # str
concept["domain_id"]       # str
concept["concept_class_id"] # str
```

## Integration Examples

### With Pandas

```python
import pandas as pd

# Search and load into DataFrame
results = client.search.basic("hypertension", page_size=100)
df = pd.DataFrame(results["concepts"])
print(df[["concept_id", "concept_name", "vocabulary_id"]].head())
```

### In Jupyter Notebooks

```python
# Iterate through all results with auto-pagination
for concept in client.search.basic_iter("diabetes", page_size=100):
    process_concept(concept)
```

## Compared to Alternatives

| Feature | OMOPHub SDK | ATHENA Download | OHDSI WebAPI |
|---------|-------------|-----------------|--------------|
| Setup time | 1 minute | Hours | Hours |
| Infrastructure | None | Database required | Full OHDSI stack |
| Updates | Automatic | Manual download | Manual |
| Programmatic access | Native Python | SQL queries | REST API |

**Best for:** Teams who need quick, programmatic access to OMOP vocabularies without infrastructure overhead.

## Documentation

- [Full Documentation](https://docs.omophub.com/sdks/python/overview)
- [API Reference](https://docs.omophub.com/api-reference)
- [Examples](https://github.com/omopHub/omophub-python/tree/main/examples)
- [Get API Key](https://dashboard.omophub.com/api-keys)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Clone and install for development
git clone https://github.com/omopHub/omophub-python.git
cd omophub-python
pip install -e ".[dev]"

# Run tests
pytest
```

## Support

- [GitHub Issues](https://github.com/omopHub/omophub-python/issues)
- [GitHub Discussions](https://github.com/omopHub/omophub-python/discussions)
- Email: support@omophub.com
- Website: [omophub.com](https://omophub.com)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built for the OHDSI community*
