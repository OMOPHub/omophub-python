# Hosted OMOP vocabulary releases for Groundworkers

Use a named OMOP vocabulary release directly from Groundworkers. OMOPHub maintains the vocabulary snapshots and serves the lookup, relationship and search requests. A team can reproduce a mapping from an older release and compare it with today's study release without downloading either snapshot, running migrations or rebuilding an embedding index.

For example, the active mapping of ICD-10-CM `D3A.022` differs between OMOPHub releases `2024.2` and `2026.2`:

| Release | Source OMOP ID | Active outgoing `Maps to` target IDs |
| --- | --- | --- |
| 2024.2 | 45537907 | 760937 |
| 2026.2 | 45537907 | 1244590, 1345982 |

## Install and connect

Use Python 3.12 or later and the Python environment that runs Groundworkers 0.11.x. From the directory containing this plugin’s `pyproject.toml`:

```sh
python -m pip install .
```

To install on another host directly from a reviewed commit, replace `COMMIT_SHA` with the full Git SHA containing this directory. Pinning the plugin commit and the vocabulary release records both pieces needed to repeat the lookup.

```sh
python -m pip install "groundworkers-omophub @ git+https://github.com/OMOPHub/omophub-python.git@COMMIT_SHA#subdirectory=plugins/groundworkers"
```

Set `OMOPHUB_API_KEY` using your credential manager and set a concrete release in the environment that starts Groundworkers. The plugin registers when both variables are present. The key’s permissions govern vocabulary access and quota. [Get an API key](https://dashboard.omophub.com) · [Available releases](https://docs.omophub.com/vocabulary-versions)

```sh
export OMOPHUB_VOCAB_RELEASE=2026.2
groundworkers --describe
```

Restart an existing MCP session after changing its configuration. To try just the hosted tools with the bundled empty SQLite host configuration, run the following from the plugin directory and connect the command as a stdio server in your MCP client.

```sh
groundworkers --config-path examples/demo.toml --transport stdio
```

Groundworkers still needs a host configuration to start. The nine `omophub_` tools read vocabulary evidence from OMOPHub. Groundworkers' native tools use the site's configured resources. Match releases before combining results from both. Each hosted call sends the exact release in the query and header and verifies the server’s release header and any release returned in metadata. An unavailable release, access denial or release mismatch produces an error.

## Compare a mapping across releases

With the host pinned to `2026.2`, call `omophub_compare_mappings`:

```json
{"vocabulary_id": "ICD10CM", "concept_code": "D3A.022", "baseline_release": "2024.2"}
```

The plugin resolves the source code independently in each release and follows every page of active outgoing `Maps to` and `Maps to value` edges. The result includes the verified release, source concept and typed target IDs for each snapshot. `added` and `removed` compare the pairs of relationship type and target concept ID. The comparison leaves the host's default pin in place for subsequent calls. If either source lookup fails or pagination is incomplete, the comparison reports an error. An empty edge list on a successful lookup means the source exists and has no active mapping of either type. Use this diff as evidence for review before changing a study definition.

## Other tools

| Tool | Use |
| --- | --- |
| `omophub_by_code` | Resolve a vocabulary ID and code on the configured release. |
| `omophub_search` | Find exact names, synonyms or codes in one vocabulary and domain. |
| `omophub_relationships` | Inspect typed edges and their original direction. Supports inbound edges and pagination. |
| `omophub_descendants` | Page through active descendants within 20 levels. Inspect `truncated` for the 5,000-row cap. |
| `omophub_fhir_resolve` | Resolve a FHIR Coding to its source and standard OMOP concepts and destination CDM table. An unmapped sentinel has concept ID 0. |
| `omophub_fhir_resolve_codeable_concept` | Resolve alternate codings for one clinical idea. Keeps the selected result, alternatives and unresolved codings. |
| `omophub_semantic_search` | Rank a terminology phrase using hosted embeddings and vocabulary/domain filters. |
| `omophub_find_similar_concepts` | Rank neighbours by lexical, semantic or hybrid similarity. Results report the algorithm used. |

Only send terminology codes or de-identified terms. Queries go to the OMOPHub API and count against the configured key. A release pin identifies the vocabulary snapshot. Search models, ranking software and access rights can change independently.

## Verify an installation

Run the offline contract tests from the plugin directory:

```sh
python -m unittest discover -s tests -v
```

With a configured API key, run the live checks through a stock Groundworkers stdio MCP host:

```sh
python examples/run_demo.py --suite omophub --release 2026.2 --output /tmp/omophub.json
python examples/run_demo.py --suite groundworkers --release 2026.2 --output /tmp/groundworkers.json
```

The first suite checks the two-release mapping diff, FHIR resolution, and hosted search. The second reproduces the published FOLFOX, family-history and ascending-colon cases. The runner returns 0 for a match, 1 for a reference difference and 2 for a case execution error. On `2026.2` the original oncology audit has a known reference difference: the published demo identifies `1077457` as a target of two benign carcinoid codes, while OMOPHub reports active targets `1244590` and `1345982`. [Groundworkers demo at the tested revision](https://github.com/AustralianCancerDataNetwork/groundworkers/blob/cc463ae1001d3e25ae471af1892ea29c0a317995/docs/demo.md)
