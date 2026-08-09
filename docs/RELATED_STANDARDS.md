# Related Standards

`mandate-schema` has a narrow purpose: governance provenance, authority, approval, versioning, effective lifecycle, and source linkage around human-approved operational mandates. The technologies and standards below address adjacent or broader concerns. These relationships do not imply equivalence, certification, or replacement.

## JSON Schema

JSON Schema defines the vocabulary used to describe and validate the structure of mandate instances. Draft 2020-12 is the canonical machine-readable format for this repository. Domain-specific lifecycle meaning and cross-field date ordering remain documented semantics layered on that structural contract.

## ODRL

The Open Digital Rights Language (ODRL) provides a model for expressing permissions, prohibitions, duties, and related policy concepts. `mandate-schema` does not reproduce that policy-expression model. It records governance and source metadata around mandate controls and can carry opaque references to rules maintained in another system.

## OSCAL

The Open Security Controls Assessment Language (OSCAL) provides models for security and privacy control information, implementation, and assessment. `mandate-schema` is not a security-control catalog or assessment model. Its control entries are limited to governance linkage identifiers and source-clause references.

## OPA and Rego

Open Policy Agent (OPA) evaluates policies written in Rego. `mandate-schema` does not define executable policies or evaluation behavior. A `rule_reference` may identify an externally maintained rule, but the reference does not embed or standardize Rego or any other expression syntax.

## FIX and FIX Orchestra

FIX supports communication in financial markets, and FIX Orchestra provides machine-readable resources for describing FIX interfaces and behavior. `mandate-schema` is not a financial transaction protocol or interface orchestration model. Its focus is the provenance and lifecycle metadata of a mandate that may govern operations elsewhere.

## FINOS Common Domain Model

The FINOS Common Domain Model provides a shared representation of financial products, trades, and lifecycle events. `mandate-schema` does not model products, transactions, or lifecycle events. It provides a narrower envelope for the governance history and references associated with human-approved mandates.

These technologies may be used independently or alongside mandate metadata where their respective scopes apply.
