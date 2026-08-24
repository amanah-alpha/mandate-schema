#!/usr/bin/env python3
"""Set-level mandate governance checks (deterministic, fail closed).

JSON Schema alone cannot express cross-document invariants. This tool
validates a SET of mandate documents for:

- unique (mandate_id, version) identity — duplicates rejected explicitly;
- self-supersession rejected;
- supersession cycles rejected (a mandate may not transitively supersede
  itself);
- inverted or zero-length effectivity windows rejected;
- timestamps end with 'Z' (UTC) — offset-local times are ambiguous across
  institutions and are rejected by policy.

Exit codes: 0 = valid set; 1 = violations found (named).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


CHECKER_VERSION = "1.0.0"


class MandateSetError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _ref_key(mandate: dict) -> tuple[str, str]:
    return (str(mandate["mandate_id"]), str(mandate["version"]))


def _require_utc_z(value: str, where: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MandateSetError(
            "NON_UTC_TIMESTAMP",
            f"{where} must be an RFC3339 UTC timestamp ending in 'Z' (got {value!r})")


def check_mandate_set(mandates: list[dict]) -> dict:
    identities: dict[tuple[str, str], dict] = {}
    edges: dict[tuple[str, str], tuple[str, str] | None] = {}

    for mandate in mandates:
        key = _ref_key(mandate)
        if key in identities:
            raise MandateSetError(
                "DUPLICATE_MANDATE_IDENTITY", f"{key[0]}@{key[1]} appears twice")
        identities[key] = mandate

        sup = mandate.get("supersedes")
        if sup is not None:
            ref = (str(sup["mandate_id"]), str(sup["version"]))
            if ref == key:
                raise MandateSetError("SELF_SUPERSESSION_REJECTED", str(key))
            edges[key] = ref

        start = mandate["effective_from"]
        _require_utc_z(start, f"{key[0]}@{key[1]}.effective_from")
        until = mandate.get("effective_until")
        if until is not None:
            _require_utc_z(until, f"{key[0]}@{key[1]}.effective_until")
            if until <= start:
                raise MandateSetError(
                    "INVERTED_EFFECTIVITY_WINDOW",
                    f"{key[0]}@{key[1]}: effective_until {until} <= effective_from {start}")

    # cycle detection over the explicit supersession graph
    for origin in sorted(edges):
        seen: set[tuple[str, str]] = set()
        current: tuple[str, str] | None = edges.get(origin)
        while current is not None:
            if current == origin:
                chain = " -> ".join(str(k) for k in (*seen, origin))
                raise MandateSetError("SUPERSESSION_CYCLE_REJECTED", chain)
            if current in seen:
                break  # cycle not involving origin; each origin is checked
            seen.add(current)
            current = edges.get(current)

    orphan_refs = sorted(
        {edges[key] for key in edges if edges[key] not in identities})
    return {
        "checker_version": CHECKER_VERSION,
        "mandate_count": len(mandates),
        "identities": sorted(f"{k[0]}@{k[1]}" for k in identities),
        "supersession_edges": sorted(f"{k[0]}@{k[1]} -> {v[0]}@{v[1]}"
                                     for k, v in edges.items()),
        "orphan_supersession_references": [
            f"{k[0]}@{k[1]}" for k in orphan_refs],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mandates", nargs="+", type=Path)
    args = parser.parse_args(argv)
    try:
        mandates = [json.loads(p.read_text(encoding="utf-8")) for p in args.mandates]
        result = check_mandate_set(mandates)
    except MandateSetError as error:
        print(json.dumps({"checked": False, "error_code": error.code,
                          "detail": error.detail}, indent=2))
        return 1
    print(json.dumps({**result, "checked": True}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
