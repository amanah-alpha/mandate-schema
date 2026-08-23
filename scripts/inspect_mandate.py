#!/usr/bin/env python3
"""Standalone mandate inspection CLI (independent of any assurance engine).

Commands:
  validate         validate a mandate JSON against the stable schema
  canonicalize     print canonical form (sorted keys, compact separators)
  digest           sha256 of the canonical form
  provenance       print authority, status, version, effectivity, supersedes

Exit 0 only when validation succeeds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_examples import build_validator  # noqa: E402


def _canonical(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "canonicalize", "digest", "provenance"):
        p = sub.add_parser(name)
        p.add_argument("mandate", type=Path)
    args = parser.parse_args(argv)

    try:
        payload = json.loads(Path(args.mandate).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        print(f"INVALID: unparseable mandate file: {error}", file=sys.stderr)
        return 1

    if args.command == "canonicalize":
        print(_canonical(payload))
        return 0
    if args.command == "digest":
        print("sha256:" + hashlib.sha256(_canonical(payload).encode()).hexdigest())
        return 0
    if args.command == "provenance":
        selected = {key: payload.get(key) for key in (
            "mandate_id", "version", "status", "authority",
            "effective_from", "effective_until", "supersedes")}
        print(json.dumps(selected, indent=2, sort_keys=True))
        return 0

    errors = sorted(build_validator().iter_errors(payload), key=lambda e: e.path)
    if errors:
        for error in errors[:5]:
            location = "/".join(str(part) for part in error.path)
            print(f"INVALID: {location}: {error.message}", file=sys.stderr)
        return 1
    print(f"VALID {payload.get('mandate_id')} v{payload.get('version')} ({payload.get('status')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
