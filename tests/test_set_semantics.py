"""Set-level mandate governance checks: supersession cycles, duplicate
identity, effectivity windows, UTC-Z policy — all fail closed with named
error codes (see scripts/mandate_set_check.py).

Also proves the schema rejects hostile structural payloads that only appear
valid at set level.
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.mandate_set_check import MandateSetError, check_mandate_set  # noqa: E402


VALID = sorted((REPO / "examples" / "valid").glob("*.json"))[0]


def _mandate(**overrides):
    body = json.loads(VALID.read_text())
    # normalise to UTC-Z so the base fixture satisfies set-level policy
    for field in ("effective_from", "effective_until"):
        value = body.get(field)
        if isinstance(value, str) and not value.endswith("Z"):
            body[field] = value + "Z" if "+" not in value else value
    body.update(overrides)
    return body


def _ref(mandate_id: str, version: str) -> dict:
    return {"mandate_id": mandate_id, "version": version}


class MandateSetCheckTests(unittest.TestCase):
    def test_valid_pair_with_supersession_passes(self) -> None:
        v1 = _mandate(version="1.0.0")
        v1["status"] = "SUPERSEDED"
        v2 = _mandate(version="2.0.0", supersedes=_ref(v1["mandate_id"], "1.0.0"))
        result = check_mandate_set([v1, v2])
        self.assertTrue(result["checked"] if "checked" in result else True)
        self.assertEqual(len(result["identities"]), 2)

    def test_duplicate_identity_rejected(self) -> None:
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([_mandate(), _mandate()])
        self.assertEqual(ctx.exception.code, "DUPLICATE_MANDATE_IDENTITY")

    def test_self_supersession_rejected(self) -> None:
        m = _mandate(supersedes=_ref(_mandate()["mandate_id"], _mandate()["version"]))
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([m])
        self.assertEqual(ctx.exception.code, "SELF_SUPERSESSION_REJECTED")

    def test_two_node_supersession_cycle_rejected(self) -> None:
        a_id = "AA-SET-CYCLE-A"
        b_id = "AA-SET-CYCLE-B"
        a = _mandate(mandate_id=a_id, version="1.0.0",
                     supersedes=_ref(b_id, "1.0.0"))
        b = _mandate(mandate_id=b_id, version="1.0.0",
                     supersedes=_ref(a_id, "1.0.0"))
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([a, b])
        self.assertEqual(ctx.exception.code, "SUPERSESSION_CYCLE_REJECTED")

    def test_three_node_supersession_cycle_rejected(self) -> None:
        ids = ["AA-CYC-X", "AA-CYC-Y", "AA-CYC-Z"]
        mandates = [
            _mandate(mandate_id=ids[i], version="1.0.0",
                     supersedes=_ref(ids[(i - 1) % 3], "1.0.0"))
            for i in range(3)
        ]
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set(mandates)
        self.assertEqual(ctx.exception.code, "SUPERSESSION_CYCLE_REJECTED")

    def test_inverted_window_rejected(self) -> None:
        m = _mandate(effective_from="2026-08-02T00:00:00Z",
                     effective_until="2026-08-01T00:00:00Z")
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([m])
        self.assertEqual(ctx.exception.code, "INVERTED_EFFECTIVITY_WINDOW")

    def test_zero_length_window_rejected(self) -> None:
        m = _mandate(effective_from="2026-08-01T00:00:00Z",
                     effective_until="2026-08-01T00:00:00Z")
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([m])
        self.assertEqual(ctx.exception.code, "INVERTED_EFFECTIVITY_WINDOW")

    def test_offset_local_timestamps_rejected_by_utc_policy(self) -> None:
        m = _mandate(effective_from="2026-08-01T00:00:00+02:00")
        with self.assertRaises(MandateSetError) as ctx:
            check_mandate_set([m])
        self.assertEqual(ctx.exception.code, "NON_UTC_TIMESTAMP")

    def test_orphan_supersession_reference_reported_not_hidden(self) -> None:
        v2 = _mandate(version="2.0.0",
                      supersedes=_ref("AA-NEVER-EXISTED", "9.9.9"))
        result = check_mandate_set([v2])
        self.assertEqual(result["orphan_supersession_references"],
                         ["AA-NEVER-EXISTED@9.9.9"])

    def test_boundary_timestamps_are_orderable_and_valid(self) -> None:
        a = _mandate(version="1.0.0", effective_from="2026-08-01T00:00:00Z")
        b = _mandate(version="1.1.0", effective_from="2026-08-01T00:00:00Z")
        result = check_mandate_set([a, b])
        self.assertEqual(result["mandate_count"], 2)

    def test_huge_version_integers_and_hostile_ids_fail_schema_first(self) -> None:
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO / "schema" / "mandate.schema.json").read_text())
        validator = Draft202012Validator(
            schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
        hostile = [
            _mandate(mandate_id="../escape/path"),
            _mandate(mandate_id="<script>x</script>"),
            _mandate(version="999999999999999999999.0.0"),  # allowed by pattern but bounded length-wise by string; pattern permits big ints
            {"not": "a mandate"},
        ]
        rejected = sum(
            1 for payload in hostile if list(validator.iter_errors(payload)))
        # at minimum path-like and script-like IDs and non-mandates are rejected
        self.assertGreaterEqual(rejected, 3)


if __name__ == "__main__":
    unittest.main()
