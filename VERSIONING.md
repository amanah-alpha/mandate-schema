# Versioning Policy

This repository distinguishes the version of the public schema specification from the version of a governed mandate instance.

## Schema and repository releases

Repository releases use semantic versioning in `MAJOR.MINOR.PATCH` form:

- **MAJOR**: an incompatible change to the public schema contract;
- **MINOR**: a backward-compatible addition or capability; and
- **PATCH**: a backward-compatible correction or clarification.

The canonical schema's `$id` includes its schema release version. A new published schema version receives a new `$id`; an already released schema is not silently replaced with incompatible content.

## Mandate instance versions

`mandate.version` is the version of a governed mandate instance. It is assigned by the mandate's governance process and is not necessarily the release version of this repository or schema. For example, mandate version `3.2.1` can validate against schema release `0.1.0`.

The `supersedes` object identifies the prior mandate by `mandate_id` and mandate-instance `version`. It does not point to a schema release.

## Breaking schema changes

Changes that generally require a schema major release include:

- adding a required property to existing instances;
- removing or renaming a property;
- narrowing an accepted type, pattern, format, or enumeration;
- changing the meaning of an existing property; or
- changing lifecycle semantics in a way that invalidates previously conforming instances.

## Non-breaking schema changes

Changes that may be backward-compatible include:

- adding an optional property without changing existing semantics;
- broadening an accepted value set where doing so preserves meaning;
- adding new valid examples or conformance cases; and
- correcting documentation without altering the machine-readable contract.

Whether a change is breaking is determined by its effect on conforming consumers and instances, not merely by its textual size.

## Deprecation policy

When practical, a field or value will be documented as deprecated in a minor release before removal in a future major release. Deprecation notices will identify the replacement, migration guidance, and the earliest release in which removal may occur. Security or correctness issues may require a faster change, which will be explained in the changelog.

Backward compatibility is preferred where practical, but deprecated behavior is not retained indefinitely when it would make the contract misleading or unsafe.
