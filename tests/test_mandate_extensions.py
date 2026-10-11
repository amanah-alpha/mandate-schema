"""Experimental mandate extension tests (R&D, QFC alignment / PDR-0001).

Pins the composable opt-in fields: assetClassScope (closed vocabulary,
unique, bounded) and the extended-control enforcement policy trio.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "experimental" / "mandate-extensions.schema.json"

QFC_SCOPE = ["PERMITTED_TOKEN_RWA", "SUKUK_CERTIFICATE", "TOKENIZED_FUND_UNIT"]


@unittest.skipIf(jsonschema is None, "jsonschema not installed")
class MandateExtensionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    def _validate(self, section: str, payload: dict) -> None:
        jsonschema.validate(payload, self.schema["$defs"][section])

    def test_qfc_scope_validates(self) -> None:
        self._validate("assetClassScopeExtension", {"asset_class_scope": QFC_SCOPE})

    def test_empty_scope_is_rejected(self) -> None:
        with self.assertRaises(jsonschema.ValidationError):
            self._validate("assetClassScopeExtension", {"asset_class_scope": []})

    def test_duplicate_scope_entries_are_rejected(self) -> None:
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(
                "assetClassScopeExtension",
                {"asset_class_scope": ["SUKUK_CERTIFICATE", "SUKUK_CERTIFICATE"]},
            )

    def test_unknown_class_is_rejected(self) -> None:
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(
                "assetClassScopeExtension",
                {"asset_class_scope": ["PERMITTED_TOKEN_RWA", "MEMECOIN"]},
            )

    def test_enforcement_requires_enabled_flag_shape(self) -> None:
        self._validate(
            "extendedControlsExtension",
            {"extended_controls_enabled": True, "extended_enforcement": "ADVISORY"},
        )
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(
                "extendedControlsExtension",
                {"extended_controls_enabled": False, "extended_enforcement": "DENY"},
            )

    def test_enforcement_trio_is_the_only_allowed_modes(self) -> None:
        for mode in ("ADVISORY", "REVIEW", "DENY"):
            self._validate(
                "extendedControlsExtension",
                {"extended_controls_enabled": True, "extended_enforcement": mode},
            )
        with self.assertRaises(jsonschema.ValidationError):
            self._validate(
                "extendedControlsExtension",
                {"extended_controls_enabled": True, "extended_enforcement": "BLOCK"},
            )


if __name__ == "__main__":
    unittest.main()
