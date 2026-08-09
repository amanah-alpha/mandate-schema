import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_examples import (  # noqa: E402
    MANIFEST_PATH,
    SCHEMA_PATH,
    build_validator,
    diagnostics,
    fixture_path,
    load_json,
    load_manifest,
    load_schema,
    schema_diagnostics,
    semantic_diagnostics,
)


class MandateExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema()
        cls.validator = build_validator(cls.schema)
        cls.manifest = load_manifest()
        cls.minimal = load_json(ROOT / "examples" / "valid" / "minimal.json")

    def test_canonical_schema_parses_and_declares_draft_2020_12(self):
        with SCHEMA_PATH.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        self.assertEqual(
            parsed["$schema"],
            "https://json-schema.org/draft/2020-12/schema",
        )

    def test_all_valid_fixtures_validate(self):
        for case in self.manifest["cases"]:
            if case["expected"] == "valid":
                with self.subTest(fixture=case["fixture"]):
                    self.assertEqual(
                        diagnostics(load_json(fixture_path(case)), self.validator),
                        [],
                    )

    def test_each_invalid_fixture_fails_for_its_intended_invariant(self):
        for case in self.manifest["cases"]:
            if case["expected"] == "invalid":
                with self.subTest(fixture=case["fixture"]):
                    found = diagnostics(load_json(fixture_path(case)), self.validator)
                    self.assertEqual([item.code for item in found], [case["expected_error"]])

    def test_semantic_version_pattern(self):
        for version in ("0.0.1", "1.0.0", "12.34.56"):
            instance = copy.deepcopy(self.minimal)
            instance["version"] = version
            with self.subTest(version=version):
                self.assertEqual(schema_diagnostics(instance, self.validator), [])

        for version in ("1", "1.0", "01.0.0", "1.0.0-beta"):
            instance = copy.deepcopy(self.minimal)
            instance["version"] = version
            with self.subTest(version=version):
                codes = [item.code for item in schema_diagnostics(instance, self.validator)]
                self.assertEqual(codes, ["schema.pattern.version"])

    def test_lifecycle_status_enum(self):
        for status in ("DRAFT", "APPROVED", "SUPERSEDED", "WITHDRAWN"):
            instance = copy.deepcopy(self.minimal)
            instance["status"] = status
            with self.subTest(status=status):
                self.assertEqual(schema_diagnostics(instance, self.validator), [])

        instance = copy.deepcopy(self.minimal)
        instance["status"] = "PUBLISHED"
        self.assertEqual(
            [item.code for item in schema_diagnostics(instance, self.validator)],
            ["schema.enum.status"],
        )

    def test_sha256_digest_pattern(self):
        valid = copy.deepcopy(self.minimal)
        valid["provenance"]["content_digest"] = "sha256:" + "0" * 64
        self.assertEqual(schema_diagnostics(valid, self.validator), [])

        for digest in ("sha256:" + "0" * 63, "sha256:" + "A" * 64, "md5:" + "0" * 64):
            instance = copy.deepcopy(self.minimal)
            instance["provenance"]["content_digest"] = digest
            with self.subTest(digest=digest):
                self.assertEqual(
                    [item.code for item in schema_diagnostics(instance, self.validator)],
                    ["schema.pattern.content_digest"],
                )

    def test_mandate_instance_version_is_independent_from_schema_release(self):
        instance = copy.deepcopy(self.minimal)
        instance["version"] = "9.8.7"
        schema_release = self.schema["$id"].rsplit(":", 1)[-1]
        self.assertNotEqual(instance["version"], schema_release)
        self.assertEqual(diagnostics(instance, self.validator), [])

    def test_effective_date_semantic_check_rejects_inverted_interval(self):
        instance = copy.deepcopy(self.minimal)
        instance["effective_from"] = "2026-06-01T00:00:00Z"
        instance["effective_until"] = "2026-05-31T23:59:59Z"
        self.assertEqual(schema_diagnostics(instance, self.validator), [])
        self.assertEqual(
            [item.code for item in semantic_diagnostics(instance)],
            ["semantic.effective_window"],
        )


if __name__ == "__main__":
    unittest.main()
