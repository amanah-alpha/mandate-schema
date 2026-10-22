"""Draft 2020-12 validation plus the documented mandate effectivity check."""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, Iterable, List
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
from ._json import check_tree


def _schema_path():
    bundled = files(__package__).joinpath("schemas", "mandate.schema.json")
    if bundled.is_file():
        return bundled
    return Path(__file__).resolve().parents[1] / "schema" / "mandate.schema.json"


@dataclass(frozen=True)
class Diagnostic:
    """A stable code paired with a human-readable validation message."""

    code: str
    message: str
    path: str = ""


def load_schema() -> Dict[str, Any]:
    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
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
        key=lambda error: (_json_pointer(error.absolute_path), str(error.validator), error.message),
    )
    return [
        Diagnostic(
            code=_schema_error_code(error),
            path=_json_pointer(error.absolute_path),
            message=f"{_json_pointer(error.absolute_path) or '/'}: {error.message}",
        )
        for error in errors
    ]


def _parse_rfc3339(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
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
                        path="/effective_until",
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
    check_tree(instance)
    structural = schema_diagnostics(instance, validator)
    if structural:
        return structural
    return semantic_diagnostics(instance)

