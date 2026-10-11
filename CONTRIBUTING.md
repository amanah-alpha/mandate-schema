# Contributing to mandate-schema

Thank you for considering a contribution. This repository owns the
**governance metadata contract** for human-approved operational mandates:
versioning, authority and approval provenance, and lifecycle state.

## Ground rules

1. **Additive-first.** The stable schema (`schema/mandate.schema.json`) is a
   public contract: new fields are added as OPTIONAL with a MINOR version
   bump; removing or re-typing an existing field is a MAJOR change and
   requires a decision record.
2. **Grammar stays shared.** Identifiers, semver, digest strings and
   lifecycle enums mirror `schema_constraints.py` in the amanah-alpha
   repository. Changes here must be mirrored there in the same release.
3. **No rule content.** This repo carries governance METADATA structure —
   never Sharia interpretations, thresholds or asset lists. Those are
   institution-authored data.
4. **Every behavior has a test.** PRs without a failing-test-first (or a
   regression test) will be asked to add one.

## Workflow

```bash
git clone https://github.com/amanah-alpha/mandate-schema.git
cd mandate-schema
python3 -m pip install -e .[test]     # or: python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q                  # full suite must pass before you push
```

- Branch from `main`; keep one logical change per PR.
- CI runs pytest + schema-validation on Python 3.11/3.12/3.13 — it must be
  green before review.
- Commit style: `type(scope): summary` (feat/fix/docs/test/chore).

## Reporting issues

Open a GitHub issue with: expected behavior, actual behavior, the minimal
schema payload that reproduces it, and your Python version. Security issues
go through Private Vulnerability Reporting (see SECURITY.md), never public
issues.
