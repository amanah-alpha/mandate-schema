# Changelog

All notable changes to this public specification will be documented in this file.

The format is based on Keep a Changelog, and repository/schema releases follow the principles in [`VERSIONING.md`](VERSIONING.md).

## [Unreleased]

## [0.1.0] - 2026-08-09

### Added

- Initial JSON Schema Draft 2020-12 mandate metadata model.
- Synthetic valid and intentionally invalid conformance fixtures.
- Reference validation script and focused test suite.
- Model, versioning, related-standards, non-goals, security, and conformance documentation.

## Unreleased — independent consumer tooling

- Add an installable Python package and CLI with bundled canonical schemas.
- Share validation between repository checks, the Python API and legacy inspectors.
- Reject duplicate keys, non-finite values, malformed input and oversized/deep files.
- Validate documents before displaying metadata or producing digests; mandate
  inspection also enforces the documented effective-date semantic check.
- Add JSON diagnostics, consumer regression tests and clean-wheel verification.
- Preserve canonical schema bytes and existing synthetic fixtures. This changes
  inspection behavior for invalid documents, not the public schema contract.
