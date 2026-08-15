# Security policy

This repository is a research reference, not a production vault, KMS, consent service, clinical system, or autonomous deployment controller.

Do not store real secrets or personal data in it. The local `SovereignVault` demonstrates one authorized envelope-decryption path; it does not protect against compromised endpoints, administrators, root access, malicious builds, screenshots, copied plaintext, unmanaged backups, side channels, denial of service, or exfiltrated keys.

The code is in research-preview status. If private vulnerability reporting is available in the GitHub Security tab, use it. Otherwise open a public issue containing no exploit details and request a private contact channel.

The minimal ledger is hash-linked but has no signing key or external head anchor in this preview. It detects in-place alteration when compared with a retained head; an actor able to rewrite the complete ledger, recompute every hash, and replace the trusted head is outside the implemented guarantee.

The reference `resource_commitment()` is a deterministic domain-separated SHA-256 digest. It does **not** anonymize a low-entropy identifier and can remain correlatable or vulnerable to dictionary guessing. Real deployments must use random high-entropy identifiers or a keyed construction such as HMAC with managed key rotation. The public fixture uses synthetic identifiers only.

A `ConsentGrant` is signed, not encrypted. Its fields are visible to anyone holding the token and must not contain private-state text, secrets, or sensitive real-world identifiers.
