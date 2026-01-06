# OMOPHub Python SDK

**Query millions standardized medical concepts via simple Python API**

Access SNOMED CT, ICD-10, RxNorm, LOINC, and 90+ OHDSI ATHENA vocabularies without downloading, installing, or maintaining local databases.

[![PyPI version](https://badge.fury.io/py/omophub.svg)](https://pypi.org/project/omophub/)
[![Python Versions](https://img.shields.io/pypi/pyversions/omophub.svg)](https://pypi.org/project/omophub/)
[![Codecov](https://codecov.io/gh/omopHub/omophub-python/branch/main/graph/badge.svg)](https://app.codecov.io/gh/omopHub/omophub-python?branch=main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

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
| `search` | Full-text and semantic search | `basic()`, `advanced()`, `semantic()`, `fuzzy()` |
| `hierarchy` | Navigate concept relationships | `ancestors()`, `descendants()` |
| `mappings` | Cross-vocabulary mappings | `get()`, `map()` |
| `vocabularies` | Vocabulary metadata | `list()`, `get()`, `stats()` |
| `domains` | Domain information | `list()`, `get()`, `concepts()` |

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
