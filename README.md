# mandate-schema

**Vendor-neutral schema for provenance, versioning, authority and approval metadata of human-approved operational mandates.**

Public interoperability specification · JSON Schema Draft 2020-12

[![CI](https://github.com/amanah-alpha/mandate-schema/actions/workflows/ci.yml/badge.svg)](https://github.com/amanah-alpha/mandate-schema/actions/workflows/ci.yml)

This project does not define a universal policy language or executable compliance engine. It models governance metadata around human-approved mandates and their referenced controls.

## 1. Purpose

`mandate-schema` provides a small, independently consumable contract for exchanging the identity, lifecycle, authority, approval, source provenance, and control linkage metadata of an operational mandate.

The canonical machine-readable artifact is [`schema/mandate.schema.json`](schema/mandate.schema.json).

## 2. Scope

The model covers:

- stable mandate identity and mandate-instance version;
- a deliberately small lifecycle status set;
- the governance authority responsible for approval;
- effective dates and an optional reference to a superseded mandate version;
- source-document, clause, and content-digest provenance;
- approval records and opaque reviewer references; and
- references connecting public controls to source clauses and external rule identifiers.

`rule_reference` is an opaque linkage identifier. It is not executable policy code, and this repository does not define the evaluator or expression syntax behind it. A content digest detects whether bytes match a known digest; it does not establish the truth, authority, or authenticity of an external source document.

## 3. Quick Example

```json
{
  "mandate_id": "mandate:synthetic:operations:001",
  "version": "1.0.0",
  "status": "APPROVED",
  "authority": {
    "authority_id": "authority:synthetic:governance:001",
    "authority_type": "INTERNAL_GOVERNANCE_BODY",
    "display_name": "Synthetic Operations Governance Committee"
  },
  "effective_from": "2026-01-01T00:00:00Z",
  "provenance": {
    "document_id": "document:synthetic:operations-manual",
    "document_version": "1.0",
    "clause_reference": "section-4.1",
    "content_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "approval": {
    "approval_id": "approval:synthetic:001",
    "approved_at": "2025-12-15T10:30:00Z",
    "reviewer_refs": ["reviewer:opaque:001"],
    "approval_reference": "record:synthetic:approval:001"
  },
  "controls": [
    {
      "control_id": "control:synthetic:operations:001",
      "source_clause": "section-4.1",
      "rule_reference": "rule-ref:synthetic:operations:001",
      "status": "ACTIVE"
    }
  ]
}
```

All examples are synthetic. See [`examples/valid`](examples/valid) for complete valid instances, including an explicitly non-authoritative digital-asset example.

## 4. Model

The model and its structural-versus-semantic validation boundary are described in [`docs/MODEL.md`](docs/MODEL.md).

## 5. Validation

Validation uses Python's mature `jsonschema` library because the Python standard library does not implement JSON Schema Draft 2020-12. The validator checks the schema against its metaschema, validates every fixture, confirms each invalid fixture's intended error, and performs the documented effective-date semantic check.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_examples.py
python -m unittest discover -s tests -v
```

The conformance inventory is [`conformance/manifest.json`](conformance/manifest.json). See [`conformance/README.md`](conformance/README.md) for the case contract.

## 6. Versioning

Repository/schema evolution and mandate-instance versioning are separate concerns. See [`VERSIONING.md`](VERSIONING.md).

## 7. Related Standards

The relationship to JSON Schema, ODRL, OSCAL, OPA/Rego, FIX/FIX Orchestra, and FINOS Common Domain Model is discussed in [`docs/RELATED_STANDARDS.md`](docs/RELATED_STANDARDS.md).

## 8. Non-Goals

The explicit boundaries of this specification are listed in [`docs/NON_GOALS.md`](docs/NON_GOALS.md).

## 9. Amanah Alpha Relationship

Amanah Alpha uses the public mandate model as an interoperability surface in its public technical work. Production mandate compilation, institution-specific rules and methodology mappings are outside this repository.

## 10. Security

Schema validation is not authorization, approval verification, or source authentication. Security considerations and vulnerability reporting guidance are in [`SECURITY.md`](SECURITY.md).

## 11. License

Licensed under the Apache License 2.0. See [`LICENSE`](LICENSE).

## Independent consumer tools

Install this repository with `python -m pip install .` to use the `mandate-schema`
command and the `mandate_schema` Python API without the Amanah Alpha evaluator.
See [the consumer guide](docs/CONSUMER_GUIDE.md) for strict file validation,
JSON diagnostics, digest limitations and clean-wheel verification.
