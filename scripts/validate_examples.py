#!/usr/bin/env python3
"""Validate the mandate schema and its conformance fixtures."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "mandate.schema.json"
MANIFEST_PATH = ROOT / "conformance" / "manifest.json"


@dataclass(frozen=True)
class Diagnostic:
    """A stable code paired with a human-readable validation message."""

    code: str
    message: str


def load_json(path: Path) -> Any:
    """Load strict JSON and add the path to parse errors."""

    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error


def load_schema() -> Dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return schema


def build_validator(schema: Dict[str, Any] | None = None) -> Draft202012Validator:
    canonical_schema = schema if schema is not None else load_schema()
    return Draft202012Validator(
        canonical_schema,
        format_checker=FormatChecker(),
    )


def _json_pointer(parts: Iterable[Any]) -> str:
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped) if escaped else ""


def _schema_error_code(error: ValidationError) -> str:
    path = list(error.absolute_path)

    if error.validator == "required" and isinstance(error.instance, dict):
        missing = [name for name in error.validator_value if name not in error.instance]
        if len(missing) == 1:
            return f"schema.required.{missing[0]}"

    field = str(path[-1]) if path else "root"
    return f"schema.{error.validator}.{field}"


def schema_diagnostics(
    instance: Dict[str, Any],
    validator: Draft202012Validator | None = None,
) -> List[Diagnostic]:
    active_validator = validator if validator is not None else build_validator()
    errors = sorted(
        active_validator.iter_errors(instance),
        key=lambda error: (list(error.absolute_path), str(error.validator), error.message),
    )
    return [
        Diagnostic(
            code=_schema_error_code(error),
            message=f"{_json_pointer(error.absolute_path) or '/'}: {error.message}",
        )
        for error in errors
    ]


def _parse_rfc3339(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def semantic_diagnostics(instance: Dict[str, Any]) -> List[Diagnostic]:
    """Apply documented cross-field checks that JSON Schema does not express."""

    effective_from = instance.get("effective_from")
    effective_until = instance.get("effective_until")
    if isinstance(effective_from, str) and isinstance(effective_until, str):
        try:
            if _parse_rfc3339(effective_until) < _parse_rfc3339(effective_from):
                return [
                    Diagnostic(
                        code="semantic.effective_window",
                        message="/effective_until: must not precede /effective_from",
                    )
                ]
        except ValueError:
            # Draft 2020-12 format validation reports malformed date-time values.
            pass
    return []


def diagnostics(
    instance: Dict[str, Any],
    validator: Draft202012Validator | None = None,
) -> List[Diagnostic]:
    structural = schema_diagnostics(instance, validator)
    if structural:
        return structural
    return semantic_diagnostics(instance)


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


def validate_repository() -> List[str]:
    """Validate all JSON, the canonical schema, and every conformance case."""

    json_paths = sorted(ROOT.rglob("*.json"))
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
