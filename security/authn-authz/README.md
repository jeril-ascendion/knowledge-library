# Authentication & Authorization

> **Section:** `security/` | **Subsection:** `authn-authz/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

OAuth 2.0, OIDC, SAML, RBAC, ABAC, fine-grained authorization, and identity federation patterns.

This document is part of the **Security Architecture** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Authentication and Authorization are Separate Concerns

Authentication establishes who you are. Authorization determines what you can do. Never conflate the two in code — authenticate at the API gateway, authorize within each service using a policy engine.

### 2. Token Lifetimes Must Match Risk Level

Access tokens for financial operations: 5 minutes. Standard API access tokens: 15–60 minutes. Refresh tokens: 7 days with single-use rotation. Longer lifetimes increase breach blast radius; shorter lifetimes increase token refresh overhead.

### 3. Centralize Identity, Federate Authorization

One Identity Provider for authentication. Per-service authorization policy enforcement. Never replicate user management logic across services — it diverges immediately.

### 4. PKCE is Mandatory for Public Clients

Any client that cannot securely store a client secret (SPAs, mobile apps) must use PKCE. Without PKCE, authorization codes can be intercepted and exchanged by an attacker.

### 5. Never Implement Custom Authentication

Use battle-tested libraries and standards. Custom JWT validation routines contain subtle vulnerabilities (algorithm confusion attacks, missing audience validation, improper expiry checking) that take years to surface and can be catastrophic.


---

## Implementation Guide

**Step 1: Select and Deploy an Identity Provider**

Choose an IdP appropriate to your context: Keycloak (self-hosted, open source, strong for regulated environments), AWS Cognito (managed, tight AWS integration), Azure AD B2C (enterprise identity federation), or Okta (enterprise SSO). Document the choice in an ADR with alternatives considered.

**Step 2: Design OAuth 2.0 Flows per Client Type**

Map each client type to its flow: SPA → Authorization Code + PKCE. Mobile → Authorization Code + PKCE. Server-side web → Authorization Code. Service-to-service → Client Credentials. CLI → Device Code. Document all flows with sequence diagrams.

**Step 3: Implement Fine-Grained Authorization with OPA**

Deploy OPA as a sidecar or centralized policy service. Write authorization policies in Rego. Express policies as: subject (who) + resource (what) + action (how) + context (when/where). Test policies with OPA's built-in test framework. Version-control policies alongside application code.

**Step 4: Configure Token Lifetimes and Rotation**

Access tokens: 15 minutes default (5 minutes for financial operations). Refresh tokens: 7 days with single-use rotation (old refresh token revoked when a new one is issued). Implement refresh token rotation to detect token theft.

**Step 5: Implement MFA for High-Value Operations**

MFA must be required for: all administrative access, financial transaction authorization, data export, and first login from a new device. Support authenticator apps (TOTP), WebAuthn/Passkeys (most phishing-resistant), and SMS OTP (last resort — vulnerable to SIM swap attacks).


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| IdP Selection ADR Completed | Security Architect | Identity provider selected, documented, and approved | Required |
| OAuth 2.0 Flow Diagrams Reviewed | Security Architect | All client type flows documented and approved | Required |
| PKCE Implemented for Public Clients | AppSec Engineer | PKCE enforced for all SPA and mobile clients verified | Required |
| OPA Policies in Version Control | Security Engineer | All authorization policies in Git with test coverage | Required |
| MFA Enforced for Admin Access | Security Engineer | MFA required for all administrative and privileged operations | Required |


---

## Recommended Patterns

### OAuth 2.0 + OIDC with PKCE

The industry standard for user authentication in web and mobile applications. Delegates identity management to a specialized IdP, supports MFA, enables single sign-on, and produces standardized JWT tokens consumable by any service.

### Policy-as-Code with OPA

Authorization policies expressed in Rego, stored in Git, tested in CI, deployed as a sidecar to each service. Enables consistent, auditable, version-controlled authorization logic across a polyglot microservices landscape.

### Token Introspection for Revocation

Instead of trusting JWT expiry alone, services call the authorization server's introspection endpoint to validate tokens in real time. Enables immediate revocation at the cost of per-request latency (mitigated with local caching of introspection results).

### Just-In-Time (JIT) Privileged Access

Administrative access is provisioned on-demand for a specific operation and time window (e.g., 2-hour production database access). Automated provisioning via PIM (Azure), IAM Access Analyzer, or CyberArk. Access is automatically revoked when the window expires.


---

## Anti-Patterns to Avoid

### ⚠️ Long-Lived Static API Keys

API keys that never expire, are shared across environments, and are stored in configuration files. A single key leak provides indefinite access. Replace with short-lived tokens issued by an IdP, or with workload identity (IAM roles, managed identities) for service-to-service authentication.

### ⚠️ Role Explosion

Creating a new RBAC role for every combination of permissions requested by every team. Organizations with 500+ roles have no operational visibility into effective permissions. ABAC with OPA scales where RBAC cannot.

### ⚠️ Ambient Network Trust

Trusting requests from internal networks without authentication. 'It's behind our firewall' is not an access control. Internal lateral movement in breaches exploits exactly this assumption. Implement Zero Trust: authenticate every request regardless of origin.


---

## AI Augmentation Extensions

### Anomalous Access Detection

ML models trained on historical access logs learn normal patterns per user and service account. Deviations — unusual access times, unfamiliar resource types, high-volume access — trigger real-time security alerts.

> **Note:** Tune anomaly detection with 90 days of baseline data before enabling automated account suspension. False positives from under-tuned models erode trust in the system.

### AI-Generated OPA Policy Drafts

LLM agents translate natural-language access control requirements ('Finance users can read but not export P&L reports outside business hours') into Rego policy drafts with test cases.

> **Note:** All AI-generated Rego policies must be reviewed by a security engineer before deployment. LLMs can generate syntactically correct but semantically incorrect policies.


---

## Related Sections

[`security/encryption`](../security/encryption) | [`security/cloud`](../security/cloud) | [`patterns/security`](../patterns/security) | [`compliance/pci-dss`](../compliance/pci-dss) | [`compliance/bsp-afasa`](../compliance/bsp-afasa)

---

## References

1. [OAuth 2.0 Security Best Current Practice — IETF](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics) — *datatracker.ietf.org*
2. [NIST SP 800-63B — Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html) — *pages.nist.gov*
3. [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/) — *openpolicyagent.org*
4. [Zero Trust Networks — Gilman & Barth](https://www.oreilly.com/library/view/zero-trust-networks/9781491962183/) — *O'Reilly*
5. [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — *csrc.nist.gov*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `security/authn-authz/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
