# Dependency Governance

> **Section:** `technology/mobile/dependency-governance/`
> **Alignment:** OWASP Dependency Check | SBOM (NTIA) | SPDX | CycloneDX | Supply Chain Security
> **Audience:** Security Architects · Mobile Architects · Engineering Leads · Compliance Officers

Every third-party library added to a mobile application is a potential attack vector, a legal liability, a maintenance obligation, and a performance cost. Mobile applications are uniquely exposed to supply chain attacks: a compromised SDK distributed through a package repository can affect millions of users across all applications that include it. Dependency governance is the systematic process of evaluating, approving, monitoring, and retiring third-party dependencies.

## Overview

Dependency governance applies across the full lifecycle of a dependency: evaluation before adoption, approval before first use, monitoring for vulnerabilities and licence changes after adoption, and planned retirement when alternatives become superior or the dependency is abandoned. The governance process is lightweight enough to accommodate normal development velocity while providing the oversight required for regulated industries.

## Dependency Evaluation Criteria

Before a new dependency is added to any Ascendion mobile project, evaluate it against six criteria:

**1. Necessity:** Does this dependency solve a problem that cannot be solved acceptably in 40 hours of custom implementation? If the dependency provides 500 lines of genuinely complex logic (cryptography, complex parsing, platform-specific hardware integration), adoption is justified. If it wraps 20 lines of standard library code, build the 20 lines.

**2. Security Posture:** Check for known CVEs (OWASP Dependency Check), review the project's security disclosure policy, verify recent security audit history for SDKs handling sensitive data (payment SDKs, identity SDKs). Reject dependencies with unpatched P1/P2 CVEs.

**3. Maintenance Activity:** Last commit date, issue resolution velocity, open critical issues, responsive maintainers. A dependency with no commits in 18 months and 50 open issues is a liability regardless of its current functionality.

**4. Licence Compatibility:** Verify the licence is compatible with the project's licence and the client's commercial terms. GPL/AGPL licences require the entire application source to be open-sourced — incompatible with proprietary commercial applications. MIT, Apache 2.0, and BSD are generally safe.

**5. Size Impact:** Mobile applications have install size budgets. An SDK that adds 3MB to an APK or IPA must justify that cost with commensurate value. Use tools: Android Studio APK Analyser, iOS App Thinning report.

**6. Privacy Implications:** SDKs that collect analytics data, advertising identifiers, or behavioural telemetry require privacy impact assessment and disclosure in the App Store privacy nutrition label. For regulated industries, third-party analytics SDKs may require explicit user consent.

## Approval Process

All new dependencies pass through the Dependency Review Gate before first commit:
1. Engineer proposes dependency with evaluation criteria completed
2. Tech Lead reviews and approves for standard dependencies (MIT/Apache, no CVEs, active maintenance)
3. Security Architect reviews for security-sensitive dependencies (authentication, cryptography, payment)
4. ARB reviews for dependencies with GPL licences, privacy implications in regulated apps, or size impact above 1MB

## Continuous Monitoring

Dependabot configured on all repositories: scans for new CVEs daily, opens PRs for security updates automatically. SLA for security updates: P1 (CVSS 9.0+) within 72 hours, P2 (CVSS 7.0-8.9) within 1 week, P3 within 1 month. SBOM (Software Bill of Materials) generated at each release using CycloneDX, stored in the release artefact registry.

## Anti-Patterns to Avoid

> **⚠ Dependency as Default Reflex** — Adding a library as the first response to any new requirement without evaluating whether the standard library or existing dependencies already cover the need.
> **CORRECT:** Check existing dependencies first. Check the standard library. Implement from scratch if the implementation is under 40 hours and the logic is not cryptographic or hardware-specific. Document the build-vs-adopt decision in the ticket.

> **⚠ Ignoring Transitive Dependencies** — Auditing direct dependencies but not their transitive dependencies. The dependency you trust may depend on a compromised library.
> **CORRECT:** OWASP Dependency Check analyses the full dependency tree, including transitive dependencies. The SBOM includes all transitive dependencies.

## References

1. OWASP — Dependency Check. owasp.org/www-project-dependency-check
2. NTIA — Software Bill of Materials. ntia.gov/sbom
3. CycloneDX — SBOM Standard. cyclonedx.org
4. Google — Play SDK Index. developer.android.com/distribute/sdk-index
