#!/usr/bin/env python3
"""FHIR type interop and client connection examples (OMOPHub SDK 1.7.0+).

Two categories of functionality are shown here:

1. **Type interoperability** - the resolver accepts any Coding-like input
   via duck typing. You can pass a plain dict, omophub's lightweight
   `Coding` TypedDict, or any object exposing `.system` / `.code`
   attributes (e.g. `fhir.resources.Coding`, `fhirpy` codings). Neither
   `fhir.resources` nor `fhirpy` is a required dependency - duck typing
   handles them transparently.

2. **Connection helpers** for external FHIR clients. If you need raw
   FHIR `Parameters` / `Bundle` responses instead of the Concept
   Resolver envelope, use `client.fhir_server_url` or
   `get_fhirpy_client()` to talk to OMOPHub's FHIR Terminology Service
   directly.

For the full Concept Resolver surface (`resolve` / `resolve_batch` /
`resolve_codeable_concept`, recommendations, quality signals, async,
error handling) see `examples/fhir_resolver.py`.

Scenarios 4 and 8 require optional extras:

    pip install omophub[fhir-resources]   # for fhir.resources objects
    pip install omophub[fhirpy]           # for the pre-wired fhirpy client

Both scenarios are guarded with try/except and skip cleanly when the
extra is not installed - this script runs end-to-end without them.
"""

from __future__ import annotations

import os
from types import SimpleNamespace
from typing import TYPE_CHECKING

import omophub

if TYPE_CHECKING:
    from omophub.types.fhir import Coding

# Read from the environment so the example runs out-of-the-box:
#   export OMOPHUB_API_KEY=oh_...
# Scenario 8 (get_fhirpy_client) needs an explicit key string, so we
# materialize it once here. All other scenarios use omophub.OMOPHub()
# directly, which also picks up OMOPHUB_API_KEY.
API_KEY = os.environ.get("OMOPHUB_API_KEY", "oh_your_api_key")


# ---------------------------------------------------------------------------
# 1. coding= kwarg with a plain dict
# ---------------------------------------------------------------------------


def coding_kwarg_with_dict() -> None:
    """Pass a plain dict via the new ``coding=`` kwarg."""
    print("=== 1. coding= kwarg with a plain dict ===")

    client = omophub.OMOPHub()
    try:
        result = client.fhir.resolve(
            coding={
                "system": "http://snomed.info/sct",
                "code": "44054006",
            },
            resource_type="Condition",
        )
        res = result["resolution"]
        print(f"  Standard: {res['standard_concept']['concept_name']}")
        print(f"  Target table: {res['target_table']}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 2. coding= kwarg with omophub's Coding TypedDict
# ---------------------------------------------------------------------------


def coding_kwarg_with_typed_dict() -> None:
    """Use omophub's lightweight `Coding` TypedDict for IDE autocomplete."""
    print("\n=== 2. coding= kwarg with omophub.types.fhir.Coding ===")

    client = omophub.OMOPHub()
    try:
        coding: Coding = {
            "system": "http://loinc.org",
            "code": "2339-0",
            "display": "Glucose [Mass/volume] in Blood",
        }
        result = client.fhir.resolve(coding=coding)
        res = result["resolution"]
        print(f"  Standard: {res['standard_concept']['concept_name']}")
        print(f"  Target table: {res['target_table']}")  # "measurement"
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 3. Duck typing with a stand-in object (no external dep)
# ---------------------------------------------------------------------------


def coding_kwarg_with_duck_object() -> None:
    """Pass any object with .system / .code / .display attributes.

    This is exactly how the resolver handles `fhir.resources.Coding` and
    `fhirpy` codings under the hood - structural matching via `getattr`.
    No isinstance checks, no conversion required.
    """
    print("\n=== 3. coding= kwarg with a duck-typed object ===")

    client = omophub.OMOPHub()
    try:
        # SimpleNamespace stands in for any Coding-like class - fhir.resources,
        # fhirpy, or your own domain model.
        fake_coding = SimpleNamespace(
            system="http://snomed.info/sct",
            code="44054006",
            display="Type 2 diabetes mellitus",
        )
        result = client.fhir.resolve(coding=fake_coding)
        res = result["resolution"]
        print(f"  Standard: {res['standard_concept']['concept_name']}")
        print(f"  Concept ID: {res['standard_concept']['concept_id']}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 4. Real fhir.resources interop (optional extra)
# ---------------------------------------------------------------------------


def coding_kwarg_with_fhir_resources() -> None:
    """Interop with the real `fhir.resources` library via duck typing.

    Requires: pip install omophub[fhir-resources]
    """
    print("\n=== 4. coding= kwarg with fhir.resources objects ===")

    try:
        from fhir.resources.R4B.codeableconcept import (
            CodeableConcept as FhirCodeableConcept,
        )
        from fhir.resources.R4B.coding import Coding as FhirCoding
    except ImportError:
        print("  Skipped: pip install omophub[fhir-resources]")
        return

    client = omophub.OMOPHub()
    try:
        # Single Coding from fhir.resources
        snomed = FhirCoding(
            system="http://snomed.info/sct",
            code="44054006",
            display="Type 2 diabetes mellitus",
        )
        result = client.fhir.resolve(coding=snomed, resource_type="Condition")
        print(
            f"  From FhirCoding: {result['resolution']['standard_concept']['concept_name']}"
        )

        # Full CodeableConcept with two codings - SNOMED wins on preference
        cc = FhirCodeableConcept(
            coding=[
                FhirCoding(
                    system="http://hl7.org/fhir/sid/icd-10-cm",
                    code="E11.9",
                    display="Type 2 diabetes mellitus without complications",
                ),
                FhirCoding(
                    system="http://snomed.info/sct",
                    code="44054006",
                    display="Type 2 diabetes mellitus",
                ),
            ],
            text="Type 2 diabetes mellitus",
        )
        cc_result = client.fhir.resolve_codeable_concept(cc, resource_type="Condition")
        best = cc_result["best_match"]["resolution"]
        print(
            f"  From FhirCodeableConcept best match: [{best['source_concept']['vocabulary_id']}] {best['standard_concept']['concept_name']}"
        )
        assert best["source_concept"]["vocabulary_id"] == "SNOMED", "SNOMED should win"
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 5. Mixed batch input (dict + TypedDict + duck object)
# ---------------------------------------------------------------------------


def mixed_batch_inputs() -> None:
    """A single `resolve_batch` accepts heterogeneous coding shapes."""
    print("\n=== 5. resolve_batch with mixed input shapes ===")

    client = omophub.OMOPHub()
    try:
        typed: Coding = {"system": "http://loinc.org", "code": "2339-0"}
        duck = SimpleNamespace(
            system="http://hl7.org/fhir/sid/icd-10-cm",
            code="E11.9",
            display=None,
        )

        result = client.fhir.resolve_batch(
            [
                {"system": "http://snomed.info/sct", "code": "44054006"},  # dict
                typed,  # TypedDict
                duck,  # duck-typed object
            ],
        )
        summary = result["summary"]
        print(f"  Resolved {summary['resolved']}/{summary['total']}")
        for i, item in enumerate(result["results"], start=1):
            if "resolution" in item:
                std = item["resolution"]["standard_concept"]
                print(f"  [{i}] {std['concept_name']} ({std['vocabulary_id']})")
            else:
                print(f"  [{i}] failed: {item['error']['code']}")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 6. Explicit kwargs override coding= fields
# ---------------------------------------------------------------------------


def explicit_kwargs_override_coding() -> None:
    """Explicit `system` / `code` kwargs always win over a `coding=` input.

    Useful when you want to reuse an existing Coding-like object but
    override a single field without rebuilding the whole object.
    """
    print("\n=== 6. Explicit kwargs override coding= fields ===")

    client = omophub.OMOPHub()
    try:
        base = SimpleNamespace(
            system="http://snomed.info/sct",
            code="44054006",  # Type 2 diabetes
            display=None,
        )
        # Override the code on the fly - explicit `code` wins.
        result = client.fhir.resolve(
            coding=base,
            code="73211009",  # Diabetes mellitus (parent concept)
        )
        res = result["resolution"]
        print(f"  Resolved: {res['standard_concept']['concept_name']}")
        print("  (override code 73211009 won over base.code 44054006)")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 7. Connection helpers: fhir_server_url + get_fhir_server_url
# ---------------------------------------------------------------------------


def connection_helper_urls() -> None:
    """Inspect the FHIR base URL for external client configuration."""
    print("\n=== 7. Connection helper URLs ===")

    from omophub import get_fhir_server_url

    client = omophub.OMOPHub()
    try:
        # Property on the client returns the R4 base URL
        print(f"  client.fhir_server_url = {client.fhir_server_url}")

        # Helper function supports r4 (default), r4b, r5, r6
        for version in ("r4", "r4b", "r5", "r6"):
            print(
                f"  get_fhir_server_url({version!r:>5}) = {get_fhir_server_url(version)}"
            )
    finally:
        client.close()


# ---------------------------------------------------------------------------
# 8. Pre-wired fhirpy client (optional extra)
# ---------------------------------------------------------------------------


def fhirpy_client_helper() -> None:
    """Use `fhirpy` directly against OMOPHub's FHIR Terminology Service.

    Use the Concept Resolver (`client.fhir.resolve`) when you want
    OMOP-enriched answers - standard concept ID, CDM target table,
    mapping quality. Use `fhirpy` via `get_fhirpy_client()` when you
    need raw FHIR `Parameters` / `Bundle` responses for FHIR-native
    tooling.

    Requires: pip install omophub[fhirpy]
    """
    print("\n=== 8. get_fhirpy_client() for raw FHIR calls ===")

    try:
        from omophub import get_fhirpy_client
    except ImportError:
        print("  Skipped: pip install omophub[fhirpy]")
        return

    try:
        fhir = get_fhirpy_client(API_KEY)
    except ImportError as e:
        print(f"  Skipped: {e}")
        return

    # Example: call CodeSystem/$lookup directly.
    # fhirpy returns a FHIR Parameters resource.
    try:
        params = fhir.execute(
            "CodeSystem/$lookup",
            method="GET",
            params={
                "system": "http://snomed.info/sct",
                "code": "44054006",
            },
        )
        display = next(
            (
                p.get("valueString")
                for p in params.get("parameter", [])
                if p.get("name") == "display"
            ),
            None,
        )
        print(f"  $lookup display: {display}")
    except Exception as e:  # demo script - catch anything fhirpy raises
        print(f"  fhirpy call failed: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    coding_kwarg_with_dict()
    coding_kwarg_with_typed_dict()
    coding_kwarg_with_duck_object()
    coding_kwarg_with_fhir_resources()
    mixed_batch_inputs()
    explicit_kwargs_override_coding()
    connection_helper_urls()
    fhirpy_client_helper()
