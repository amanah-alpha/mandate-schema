# Mandate Schema — Repository Instructions

This repository is one of exactly three substantive repositories in the frozen Amanah Alpha public GitHub architecture:

- `amanah-alpha`
- `mandate-schema`
- `institutional-event-schema`

Do not create, rename, split, or propose additional repositories.

Do not introduce EvidenceOS.

## Repository Role

`mandate-schema` is an independently consumable open interoperability specification.

Its scope is:

> Vendor-neutral schema for provenance, versioning, authority, and approval metadata of human-approved operational mandates.

It is **not**:

- a universal compliance language
- a policy execution engine
- a Sharia standard
- a fatwa framework
- a replacement for OPA/Rego
- a replacement for OSCAL
- a replacement for ODRL
- a replacement for FIX
- a replacement for FINOS CDM
- the production Amanah Alpha rule model

## Canonical Format

The canonical format is:

> JSON Schema Draft 2020-12

Human-readable YAML examples may be considered later, but JSON is the canonical machine-readable representation.

Do not introduce OpenAPI unless an actual API surface exists.

## Public Scope

This repository may contain:

- mandate identity
- semantic versioning metadata
- lifecycle status
- authority references
- approval metadata
- effective dates
- supersession metadata
- source-document references
- source-clause references
- content digests
- reviewer references
- public control/rule references
- valid examples
- invalid examples
- conformance cases
- versioning policy
- related-standards documentation

## Out of Scope / Private

Never include:

- proprietary Amanah Alpha rule compilation
- production policy-engine behavior
- customer-specific mandates
- approved institutional rule libraries
- proprietary Sharia methodology mappings
- customer names or data
- regulator-specific legal interpretations presented as authoritative
- production deployment or security configuration

## Claim Discipline

Never claim:

- universal standard
- industry standard
- regulatory standard
- first
- only
- unique
- regulator approved
- Sharia approved

This is a public interoperability specification under development.

## Engineering Principles

Prefer:

- minimal schema surface
- explicit required fields
- stable identifiers
- clear lifecycle semantics
- independently testable examples
- meaningful valid/invalid conformance cases
- backward-compatible versioning where practical

Avoid:

- business logic in JSON Schema
- embedding executable rule languages
- over-modeling every possible institution
- speculative fields
- vendor-specific APIs
- schema complexity for appearance

## Before Completing Any Task

- Read this `AGENTS.md`.
- Preserve repository scope.
- Validate all JSON.
- Validate examples against the canonical schema.
- Review for misleading standardization claims.
- Review for regulatory or Sharia-authority implications.
- Report exactly what changed.
