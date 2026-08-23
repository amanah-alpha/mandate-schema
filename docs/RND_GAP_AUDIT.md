# R&D Gap Audit — mandate-schema (22 August 2026)

Audit of `main` @ `fc2fad3` prior to R&D changes.

## Already supported (verified against `schema/mandate.schema.json`)

| Concept | Status |
| --- | --- |
| Mandate identity (`mandate_id` stable identifier) | SUPPORTED |
| Strict semver versioning | SUPPORTED |
| Lifecycle status enum (DRAFT/APPROVED/SUPERSEDED/WITHDRAWN) | SUPPORTED |
| Authority block (provenance) | SUPPORTED |
| Effectivity (`effective_from`, nullable `effective_until`) | SUPPORTED |
| Supersession (`supersedes` reference) | SUPPORTED |
| Approval metadata block | SUPPORTED |
| Provenance section | SUPPORTED |
| Controls references | SUPPORTED |
| Strict unknown-field rejection, stable-id pattern, sha256 digest pattern | SUPPORTED |

## Gaps / R&D observations

1. **Revocation** — WITHDRAWN status exists; a distinct revocation timestamp
   is absent. Engine semantics (revoked packs cannot evaluate new events but
   history stays replayable) can be expressed from status + metadata as-is;
   adding a field would be MINOR — deferred pending external evidence.
2. **Supersession cycles** — JSON Schema cannot express cross-document graph
   constraints. Cycle detection belongs to the consumer engine
   (amanah-alpha graph validator already rejects cycles). Documented here;
   no schema change possible or needed.
3. **Interpretation references** — generic interpretation refs are
   representable via provenance/controls indirection; dedicated structure
   would be premature without methodology-review evidence.
4. **Canonical digest** — no canonical-form helper shipped. Added on this
   branch as an R&D CLI (`inspect_mandate.py`: canonical form + digest),
   using sorted-key compact JSON. This defines the reference profile used by
   amanah-alpha's protocol manifest.
5. **Adversarial coverage** — existing tests validate valid examples; hostile
   inputs (inverted effectivity, bad digests, wrong types) now pinned by the
   new R&D test suite.

## Versioning decision

Stable schema untouched. R&D additions: tests + tooling only.
