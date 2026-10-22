#!/usr/bin/env python3
"""Validate the mandate schema and its conformance fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "mandate.schema.json"
MANIFEST_PATH = ROOT / "conformance" / "manifest.json"


sys.path.insert(0, str(ROOT))

from mandate_schema._json import load_json_value as load_json  # noqa: E402
from mandate_schema.validation import (  # noqa: E402
    Diagnostic, build_validator, diagnostics, load_schema,
    schema_diagnostics, semantic_diagnostics,
)


def load_manifest() -> Dict[str, Any]:
    manifest = load_json(MANIFEST_PATH)
    if not isinstance(manifest, dict) or not isinstance(manifest.get("cases"), list):
        raise ValueError(f"{MANIFEST_PATH}: expected an object containing a cases array")
    return manifest


def fixture_path(case: Dict[str, Any]) -> Path:
    return (MANIFEST_PATH.parent / case["fixture"]).resolve()


def _assert_manifest_coverage(cases: Sequence[Dict[str, Any]]) -> None:
    discovered = {
        path.resolve()
        for directory in (ROOT / "examples" / "valid", ROOT / "examples" / "invalid")
        for path in directory.glob("*.json")
    }
    listed = {fixture_path(case) for case in cases}
    if discovered != listed:
        missing = sorted(str(path.relative_to(ROOT)) for path in discovered - listed)
        extra = sorted(str(path) for path in listed - discovered)
        raise ValueError(
            f"manifest fixture coverage mismatch; unlisted={missing}, unknown={extra}"
        )
    if len(listed) != len(cases):
        raise ValueError("manifest contains duplicate fixture paths")


def repository_json_paths(root: Path) -> List[Path]:
    ignored = {".git", ".venv", "build", "dist", ".pytest_cache", "__pycache__"}
    return sorted(path for path in root.rglob("*.json")
                  if not any(part in ignored or part.endswith(".egg-info")
                             for part in path.relative_to(root).parts))


def validate_repository() -> List[str]:
    """Validate all JSON, the canonical schema, and every conformance case."""

    json_paths = repository_json_paths(ROOT)
    for path in json_paths:
        load_json(path)

    schema = load_schema()
    validator = build_validator(schema)
    manifest = load_manifest()
    cases = manifest["cases"]
    _assert_manifest_coverage(cases)

    declared_schema = (MANIFEST_PATH.parent / manifest["schema"]).resolve()
    if declared_schema != SCHEMA_PATH.resolve():
        raise ValueError("manifest does not reference the canonical schema")

    output = [
        f"PASS parsed {len(json_paths)} JSON files",
        "PASS canonical schema is valid JSON Schema Draft 2020-12",
    ]

    for case in cases:
        path = fixture_path(case)
        instance = load_json(path)
        found = diagnostics(instance, validator)
        found_codes = [diagnostic.code for diagnostic in found]
        expected = case.get("expected")

        if expected == "valid":
            if found:
                details = "; ".join(
                    f"{diagnostic.code}: {diagnostic.message}" for diagnostic in found
                )
                raise ValueError(f"{path.relative_to(ROOT)}: expected valid; {details}")
            output.append(f"PASS valid   {path.relative_to(ROOT)}")
        elif expected == "invalid":
            expected_error = case.get("expected_error")
            if found_codes != [expected_error]:
                raise ValueError(
                    f"{path.relative_to(ROOT)}: expected exactly [{expected_error}], "
                    f"found {found_codes}"
                )
            output.append(
                f"PASS invalid {path.relative_to(ROOT)} -> {expected_error}"
            )
        else:
            raise ValueError(f"{path.relative_to(ROOT)}: unknown expected outcome {expected!r}")

    return output


def main() -> int:
    try:
        for line in validate_repository():
            print(line)
    except Exception as error:  # A command-line validator must fail closed.
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
