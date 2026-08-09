# Model

The mandate model describes governance provenance and lifecycle metadata around a human-approved operational mandate. It intentionally does not describe how referenced controls are executed.

## Identity and lifecycle

- `mandate_id` is a stable identifier for the mandate across versions.
- `version` is the governed mandate instance's `MAJOR.MINOR.PATCH` version. It is independent of the schema or repository release version.
- `status` is one of `DRAFT`, `APPROVED`, `SUPERSEDED`, or `WITHDRAWN`.
- `effective_from` and optional `effective_until` delimit the intended effective window.
- `supersedes`, when present, references a prior `mandate_id` and `version` without embedding the prior mandate.

The status set is deliberately small. Workflow steps, publication queues, and institution-specific approval states remain outside the base model.

## Authority

`authority` identifies the governance authority associated with approval. Its type is deliberately generic and does not presume a religious, regulatory, corporate, or public-sector authority model. `jurisdiction_reference` is an optional opaque linkage; its presence does not imply endorsement or legal effect.

## Source provenance

`provenance` links the mandate to a source document, document version, and clause reference. `content_digest` uses `sha256:` followed by 64 lowercase hexadecimal characters.

The digest supports content matching. It does not prove that the source is true, authentic, legally effective, or properly approved.

## Approval

`approval` records an opaque approval identifier, timestamp, reviewer references, and an approval-record reference. Reviewer references are opaque identifiers; names and personal information are neither required nor expected. Digital signatures and trust-chain verification are not part of this release.

## Control references

Each item in `controls` links a `control_id` to a `source_clause`, `rule_reference`, and linkage status. `rule_reference` identifies a rule maintained elsewhere. It is not an executable expression, and this schema defines no policy language, interpreter, evaluator behavior, or result semantics.

## Validation boundary

The JSON Schema validates structure, required fields, enumerations, identifier and digest patterns, and RFC 3339 `date-time` formats when used with format checking.

Cross-field temporal ordering is a semantic constraint: when `effective_until` is present and non-null, it must not precede `effective_from`. JSON Schema does not express that comparison reliably, so [`scripts/validate_examples.py`](../scripts/validate_examples.py) performs it explicitly. Consumers should apply the same check after schema validation.
