# Secure Software Development Lifecycle (SSDLC)

> **Section:** `technology/mobile/ssdlc/`
> **Alignment:** OWASP SAMM | Microsoft SDL | NIST SSDF (SP 800-218) | OWASP Mobile Top 10
> **Audience:** Security Architects · Mobile Engineers · DevOps Engineers · QA Architects

Security in mobile applications cannot be added at the end of a development cycle. By the time a penetration tester identifies a vulnerability in a finished application, the remediation cost is ten times higher than catching the same vulnerability at design time, and the damage to client trust may be irreparable in regulated industries. The Secure Software Development Lifecycle embeds security activities into every phase of engineering.

## Overview

The SSDLC for mobile has six phases, each with specific security activities, artefacts, and gates that must be completed before the next phase begins. The model follows OWASP SAMM (Software Assurance Maturity Model) adapted for the mobile delivery context, with specific integration points into Ascendion's CI/CD pipeline (defined in ADR-MOB-003).

## SSDLC Phases

### Phase 1: Security Requirements
During project inception, before the first line of code: identify the data classification (what PII, financial, or health data the app handles), determine the applicable regulatory frameworks (BSP Circular 982, PDPA, PCI-DSS, HIPAA), specify the MASVS compliance level required (L1 or L2), and document the threat model. Security requirements are recorded in the project's security requirements register and referenced in Definition of Done criteria.

### Phase 2: Secure Design
Architecture review with security focus. Threat modelling using STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) applied to the data flows identified in the C4 Context and Container diagrams. For each threat identified: likelihood rating, impact rating, and required mitigation control. The Security Architect reviews and signs off the design before development begins.

### Phase 3: Secure Coding Standards
Engineers follow mandatory secure coding standards: no hardcoded credentials (enforced by GitLeaks pre-commit hook and CI scan), parameterised SQL queries only (enforced by Room on Android), WebView JavaScript disabled unless explicitly required (enforced by Detekt rule), PII annotation on all sensitive fields (enforced by custom Detekt rule). Security-specific code review checklist covers the OWASP Mobile Top 10 controls. The first occurrence of each new security pattern is reviewed by the Security Architect.

### Phase 4: Security Testing
Automated: OWASP Dependency Check in CI (blocks on P1/P2 CVEs), Detekt security rules, SwiftLint security rules, GitLeaks secret scanning. Manual: security-focused code review for authentication flows and data storage patterns before first release. Penetration testing by an external firm (Synack, NCC Group, or equivalent) before first production release for Level 2 applications.

### Phase 5: Security in Release
Binary hardening verification in CI: confirm `debuggable: false`, confirm R8/ProGuard applied, confirm no development endpoints accessible. Privacy label accuracy verification (App Store Connect privacy nutrition label matches actual data collection). SBOM (Software Bill of Materials) generated for each release to track third-party library versions.

### Phase 6: Post-Release Security Operations
Vulnerability disclosure programme documented and published. Security monitoring: anomalous authentication patterns (unusual login locations, high failure rates), runtime integrity alerts from Play Integrity API and AppAttest. Dependency scanning continuous: Dependabot configured on the repository with P1 CVE patch SLA of 72 hours.

## Security Gates in the CI/CD Pipeline

| Gate | Phase | Tool | Action on Failure |
|---|---|---|---|
| Secret Detection | Every commit | GitLeaks | Block commit |
| Dependency CVE | Every PR | OWASP Dependency Check | Block merge on P1/P2 |
| Detekt Security Rules | Every PR | Detekt | Block merge |
| Binary Hardening | Release build | Custom CI step | Block release |
| Penetration Test | Pre-launch (L2) | External firm | Block launch |

## Anti-Patterns to Avoid

> **⚠ Security as a Pre-Launch Activity Only** — "We'll do security testing before we release." By release, there is no time to fix structural vulnerabilities. Architectural decisions made in week 1 create vulnerabilities that cannot be patched in week 12 without significant rework.
> **CORRECT:** Threat modelling in design phase. Security gates in every PR. Security Architect available for consultation throughout development, not only at the end.

> **⚠ Treating Penetration Testing as the Security Programme** — One penetration test before launch gives a point-in-time security snapshot. Dependencies added after the pentest may introduce new vulnerabilities.
> **CORRECT:** Continuous automated scanning. Penetration testing supplements, not replaces, continuous scanning and secure coding practice.

## References

1. OWASP — Software Assurance Maturity Model (SAMM). owaspsamm.org
2. NIST — Secure Software Development Framework (SP 800-218). csrc.nist.gov
3. Microsoft — Security Development Lifecycle. microsoft.com/en-us/securityengineering/sdl
4. OWASP — Mobile Application Security Testing Guide (MASTG). mas.owasp.org
