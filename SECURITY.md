# Security

## Reporting a vulnerability

Please report suspected vulnerabilities privately to the repository maintainers using the private security-reporting mechanism available on the repository host. Do not include customer data, confidential mandate content, credentials, or other sensitive material in a public issue.

If no private reporting mechanism is available, open a public issue containing only enough non-sensitive information to request a private contact channel.

## Security model

This repository defines a data validation contract. Successful schema validation means that an instance has the expected structure and value shapes; it does not establish:

- that an authority or reviewer identity is genuine;
- that an approval was authorized;
- that a referenced document is trustworthy or legally effective;
- that a control is correctly implemented or evaluated; or
- that an instance is safe to execute.

`content_digest` can be used to compare content with an expected SHA-256 digest. A matching digest does not independently prove provenance, truth, ownership, approval, or authenticity.

Consumers should establish their own trust anchors, authorization checks, secure retrieval rules, and resource limits. Treat identifiers and display strings as untrusted input when rendering, logging, indexing, or resolving references.

This repository does not contain production deployment or security configuration.
