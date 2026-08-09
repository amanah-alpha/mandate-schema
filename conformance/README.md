# Conformance Cases

[`manifest.json`](manifest.json) is the conformance inventory for this release. Each case identifies a fixture, its expected valid or invalid outcome, and one intended invariant.

Invalid fixtures are designed to violate one invariant each. `expected_error` is a stable diagnostic code emitted by the reference validator after standards-compliant JSON Schema validation or the documented effective-window semantic check.

Run all cases from the repository root:

```sh
python3 scripts/validate_examples.py
```

A conforming consumer should:

1. parse JSON without extensions;
2. validate instances against [`schema/mandate.schema.json`](../schema/mandate.schema.json) as JSON Schema Draft 2020-12, including format checking;
3. enforce the documented effective-window ordering rule; and
4. accept every valid fixture and reject every invalid fixture for its intended invariant.

Conformance with these fixtures does not verify authorization, legal effect, source authenticity, or implementation of a referenced control.
