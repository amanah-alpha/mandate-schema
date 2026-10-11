# Governance

## Roles

- **Maintainers** merge PRs, cut versions and own the contract's backward
  compatibility. Current maintainer: the amanah-alpha founding team.
- **Contributors** submit PRs and issues under the Contributing rules.

## Decision process

1. Contract changes (fields, enums, versioning) require a decision record
   in the PR description: motivation, backward-compatibility analysis, and
   the mirroring change in amanah-alpha's `schema_constraints.py`.
2. Additive changes need one maintainer approval. Breaking changes need a
   deprecation window (old form accepted for at least one MINOR release).
3. The pinned-commit protocol with amanah-alpha means schema and consumer
   move together: a schema release that breaks the family gate cannot merge.

## Versioning

Strict semver. MAJOR = breaking (field removed/re-typed, enum value
removed), MINOR = additive optional field, PATCH = documentation/clarification.

## Code of Conduct

Enforced per `CODE_OF_CONDUCT.md`; reports go to maintainers privately.
