# Security Patterns

Architecture for systems where security is a designed property of every boundary — the patterns for threat modeling, identity, defense in depth, cryptography, fail-safe behavior, and audit that turn protection from a feature added at the end into a property woven throughout.

**Section:** `patterns/` | **Subsection:** `security/`
**Alignment:** NIST CSF | ISO 27001 | OWASP | Zero Trust Architecture

---

## What "security patterns" actually means

A *security-as-feature* approach treats security as a phase of the project: design the system, build the system, then have someone review it for security before launch. This produces predictable patterns — vulnerabilities found late are expensive to fix; controls applied at the end are bolted on top of architecture that wasn't designed to receive them; the security team is positioned as the "no" department; and breaches happen along the seams the architecture made invisible.

A *security-as-architecture* approach treats security as a design property woven through the whole system from the first sketch. Threat models inform structure. Identity is a first-class boundary, not an authentication library called at the perimeter. Audit logs are designed alongside the operations they record. Cryptographic decisions are made deliberately for the specific problems they solve, by people who understand their failure modes. Failure defaults to denial. None of this is "extra work for security" — it is the work, distributed through the architecture rather than concentrated in a phase.

The architectural shift is not "we added an SSO." It is: **security is what the architecture does at every boundary, not what a team does before launch — and a system whose security is concentrated in one phase, one team, or one perimeter is a system whose security is structurally undeliverable.**

---

## Six principles

### 1. Threat modeling is the design step that prevents the most expensive incidents

Most security incidents trace back to threats that were never explicitly considered — not because the team didn't care about security, but because they never asked the systematic question of "what could go wrong here?" Threat modeling is that question, applied at design time, with a structured framework (STRIDE, PASTA, kill chain) that prevents the team from missing whole categories of risk. The cost of running a threat model is small; the cost of the incident it prevents is enormous. That asymmetry is the principle.

#### Architectural implications

- Every major capability has a documented threat model created at design time, not assembled retroactively after the first incident.
- Threats are categorized through a chosen framework (most commonly STRIDE), with each category considered explicitly rather than inferred from intuition.
- Mitigations for identified threats are tracked alongside other architectural decisions and reviewed when the design changes.
- The threat model is a living document: revisited when the system grows, when threat actors evolve, or when an incident reveals an unconsidered category.

#### Quick test

> Pick your most security-sensitive capability. Where is its threat model? If the answer is "in someone's head" or "we'd need to put one together," the most expensive failures are still on the table — the team simply hasn't been asked the question that would surface them.

#### Reference

[Adam Shostack, Threat Modeling: Designing for Security](https://shostack.org/books/threat-modeling-book) — the canonical practitioner's reference, and the book that turned threat modeling from arcane discipline into reproducible practice.

---

### 2. Least privilege is the default; broader access is the exception that requires justification

Every grant of access — every IAM policy, every database role, every API key, every service-to-service trust — is either least-privileged by design or accidentally over-privileged. There is no neutral middle. Over-privilege is silent: the access works, the application runs, no incident reports the unused permissions. But every excess permission is a foothold for an attacker who compromises that identity. Designing for least privilege is not paranoia; it is the recognition that excess permissions cost nothing to grant and become catastrophic exactly when their existence becomes visible.

#### Architectural implications

- Every identity (human user, service, machine) starts with no access; permissions are explicitly granted with documented justification.
- Time-bounded access (just-in-time, just-enough) is preferred over permanent grants where the underlying need is intermittent.
- Privilege escalation paths are designed deliberately, with explicit elevation, audit logging, and approval workflows — not improvised through informal chat-based requests.
- Periodic access reviews happen by default — privileges that haven't been used in a defined window are revoked automatically, not retained on the assumption they're still needed.

#### Quick test

> Pick a service in your production system. List the permissions it currently has, then list the permissions it actually uses. If those lists differ — and they almost always do — every unused permission is an attack surface paying compounding interest.

#### Reference

[Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege) — formalized by Saltzer and Schroeder in 1975; still the most consequential undervalued principle in security architecture.

---

### 3. Identity is the perimeter; every boundary verifies, no boundary trusts

The classic perimeter model — the network is inside, the world is outside, defense lives at the edge — has been wrong for decades and is now actively harmful. Cloud workloads, remote workers, third-party integrations, and software supply chains all dissolve the network perimeter. What remains as the unit of trust is identity: who (or what service) is making this request, with what authorization, demonstrated by what credential. Zero trust is the architectural commitment to verify identity at every boundary, not just the front door — including service-to-service traffic that the network would otherwise treat as inherently safe.

#### Architectural implications

- Every service-to-service call carries verifiable identity (signed token, mutual TLS, workload identity), validated at the receiver.
- Network position is a defense-in-depth layer, not a trust signal — being "inside" the VPC grants no special access by default.
- Authorization decisions are made at the resource based on identity and context, not at the network based on source IP.
- Identity sources (IdP, certificate authority, workload identity provider) are treated as critical infrastructure with their own security architecture, threat model, and recovery plan.

#### Quick test

> If an attacker reached one of your internal services with a valid network path, what would they need to do to access another internal service? If the answer is "nothing — internal services trust each other," the perimeter model is still in place, and one breach is the breach.

#### Reference

[NIST SP 800-207, Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — the canonical specification for the model, including the architectural shift from network-as-trust to identity-as-trust.

---

### 4. Cryptography solves narrow problems precisely; key management is the hard part

Cryptography is a set of tools, each designed to solve a specific problem: encryption (confidentiality), MAC and HMAC (integrity), digital signatures (integrity plus authenticity plus non-repudiation), TLS (confidentiality plus authenticity in transit), key derivation (a secure key from a password). Choosing the wrong tool for a problem produces a system that looks secure but isn't. Even right-sized cryptography is undermined by bad key management — keys committed to source control, keys never rotated, keys held by the same identity that uses them, keys stored alongside the data they protect. The math is rarely the weak link; the operational handling of keys almost always is.

#### Architectural implications

- Cryptographic decisions are made by understanding the problem first (confidentiality? authenticity? non-repudiation?) and then choosing the tool — not by reaching for "encryption" as a generic verb.
- Algorithm choices are reviewed against current cryptographic guidance, not frozen at the project's start and forgotten.
- Keys are stored in dedicated secret stores (HSM, KMS, sealed secrets), accessed by service identity rather than by humans, and rotated automatically.
- Certificate lifecycle (issuance, rotation, revocation) is fully automated; manual cert renewals are recognised as a category of latent incident waiting for the renewal email to be missed.

#### Quick test

> Look at your most security-sensitive secret in production. Where is it stored, when was it last rotated, and who has direct read access? If the answer involves a config file, a "we rotated it once last year," or a list of names that includes anyone who has ever worked on the system, key management is the unsolved problem behind every other security control.

#### Reference

[Latacora — Cryptographic Right Answers](https://www.latacora.com/blog/2018/04/03/cryptographic-right-answers/) — practitioner guidance on which primitives to choose for which problems, written by people who have seen the wrong answers chosen many times.

---

### 5. Fail safe, not open — security failures default to denial

When a security check fails — auth service unreachable, signature verification erroring, certificate expired, policy engine timing out — the system has a choice: deny the request or allow it. The temptation toward "fail open" is real; it preserves availability, avoids angry users, keeps SLOs intact. The result is a system whose security guarantees apply only when nothing is broken, which is exactly the moment when an attacker is most likely to be exploiting the breakage. Fail-safe — denying when uncertain — sometimes hurts availability briefly. Fail-open hurts security permanently.

#### Architectural implications

- Authentication failures result in denied access, not bypassed auth.
- Authorization service unreachable means denied operations, not implicit allow with the policy engine treated as an optimisation.
- Certificate validation failures stop the connection, not log a warning and continue.
- The failure modes of security controls are exercised in chaos testing and game days — verified in production-like conditions, not assumed.

#### Quick test

> What does your authorization system do when its policy store is unreachable? If the answer is "uses cached policy" or "allows the request through," the failure mode is fail-open and the security model rests on the policy store never being down at exactly the wrong moment.

#### Reference

[Defense in Depth (computing)](https://en.wikipedia.org/wiki/Defense_in_depth_%28computing%29) and the [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) both frame fail-safe defaults as foundational rather than optional — a position the industry has held since the original Saltzer-Schroeder paper in 1975 and has periodically forgotten under availability pressure.

---

### 6. Audit is architecture; logs are evidence

When an incident happens, the question isn't "do we have logs?" — it is "do we have logs that survive the incident, that an attacker couldn't have modified, that capture who-did-what-when in enough detail to reconstruct the event, and that are retained long enough to find lateral movement that started months ago?" Forensic readiness is a property of the architecture, designed before the breach. Logs that an attacker can edit are not logs; they are theatre. Audit trails added after the first incident are educated guesses about what mattered; audit trails designed before are evidence.

#### Architectural implications

- Authentication, authorisation, and privileged-action events are logged with structured detail — who, what, when, from where, with what credential, against what resource.
- Logs are append-only and tamper-evident: stored separately from the systems they audit, signed or hashed in ways that make modification detectable.
- Retention is defined by the longest of regulatory requirement, forensic window, and incident investigation horizon — not by storage cost optimisation.
- Log review is automated where possible (anomaly detection, alerting on privilege changes) and exercised regularly through tabletop and live drills.

#### Quick test

> If a privileged credential was misused six months ago and the attacker has since covered their tracks in the system they compromised, can you still detect it from your audit logs? If the answer is "we'd need to check whether logs from that period still exist," forensic readiness has not been engineered.

#### Reference

The [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) — the Detect and Respond functions formalise audit and forensic readiness as architectural concerns rather than as operational hygiene to be added later.

---

## Architecture Diagram

The diagram below shows a canonical security-as-architecture topology: an identity provider issues tokens; an API gateway verifies them at the perimeter; service-to-service calls carry workload identity validated at every receiver; secrets live in a dedicated store accessed by service identity; data is encrypted at rest; every authentication, authorisation, and privileged-action event flows to a tamper-evident audit log stored separately from the systems it observes.

---

## Common pitfalls when adopting security-as-architecture thinking

### ⚠️ Security as a phase, not a property

The "we'll do a security review before launch" pattern. By the time review happens, fixing the architecture costs more than rebuilding what's already there — and so most findings are deferred, accepted as risk, or papered over with compensating controls that don't really compensate.

#### What to do instead

Threat modelling at design, security review at every architectural decision, security engineers embedded in product teams rather than gatekeeping them. Security as a property of how the team works, not a phase of the project plan.

---

### ⚠️ Network as trust boundary

The legacy assumption that traffic inside the firewall is safe. It made sense when the network was the perimeter and the corporate office was the network; it has been actively harmful for at least a decade. Once the attacker is inside (and they will be — through a phishing link, a supply-chain compromise, a misconfigured cloud resource), nothing slows lateral movement.

#### What to do instead

Zero trust as the default. Every service-to-service call verified. Network segmentation kept as a defence-in-depth layer, not relied on as a trust signal. The cost of getting this right is paid once at design time; the cost of getting it wrong is paid catastrophically the first time a single workload is compromised.

---

### ⚠️ Secrets that don't rotate

The most common breach amplifier after phishing. Static credentials in CI/CD systems, in environment files, in container images, in code committed to repositories years ago. They're credentials until they're discovered, then they're a foothold — and the longer they have existed, the wider the blast radius of their discovery.

#### What to do instead

Every secret in a dedicated secret store. Every secret rotated automatically on a defined schedule. Every secret accessed by service identity rather than by humans. Secrets in source control treated as a P1 incident the moment they're detected, with the assumption they're already compromised by anyone who has ever cloned the repo.

---

### ⚠️ Compliance theatre

Performing the listed controls in a standard while missing the threats they were designed to address. The control "passwords must be rotated every 90 days" was about reducing the window of credential compromise; performing it as "users get a forced reset reminder" while leaving service accounts with permanent credentials misses the point entirely. Compliance frameworks are a floor, not a ceiling.

#### What to do instead

Use compliance frameworks as starting points for the security architecture, not as the goal. The threat model drives controls; the controls happen to satisfy compliance because they actually address threats. When a control feels "just for compliance," that's a signal to revisit the threat it was meant to address.

---

### ⚠️ Logging without protecting the logs

Audit trails an attacker can modify or delete are not audit trails. The first move of any sophisticated attacker in a compromised system is to clean their tracks — and a security architecture that didn't anticipate this has produced theatre rather than evidence.

#### What to do instead

Audit logs stored separately from the systems they observe, append-only by design, tamper-evident through cryptographic chaining or external WORM storage. The audit pipeline is itself part of the threat model — what would an attacker have to do to corrupt it, and is that path harder than the original compromise?

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | A threat model exists for each major capability, reviewed at design time and kept current ‖ Without an explicit threat model, security is reactive — the team handles whatever the latest incident teaches them. With one, the team knows what they're defending against and can choose controls deliberately, before the controls would otherwise be retrofitted under pressure. | ☐ |
| 2 | Identity verification happens at every service boundary — internal traffic is not implicitly trusted ‖ The network is not a trust boundary in modern architectures. mTLS, workload identity, signed tokens — pick a mechanism and enforce it everywhere. The cost of design discipline is far less than the cost of unrestricted lateral movement after the first breach. | ☐ |
| 3 | Least-privilege access is enforced by tooling, not by policy alone ‖ Policy that says "grant minimum access" without tooling that prevents over-grant produces the same outcome as no policy. Tooling can be IAM-as-code, automated access reviews, or just-in-time access systems — but it must be tooling, not honour system. | ☐ |
| 4 | All secrets are managed by a dedicated secret store with automatic rotation ‖ Static secrets in config files, in environment variables nobody owns, or in CI/CD systems are credentials waiting to be exfiltrated. A dedicated store with rotation is not optional infrastructure; it is core to the security architecture. | ☐ |
| 5 | Encryption-in-transit and encryption-at-rest are defaults, with documented exceptions ‖ Defaults matter more than rules. If encryption is the default and exceptions are documented, the system is encrypted by structure. If encryption is "we should encrypt the sensitive things," the system is encrypted by remembering — and people forget. | ☐ |
| 6 | Audit logs are tamper-evident, append-only, and stored separately from the systems they observe ‖ Logs that an attacker can modify are theatre. Tamper-evidence (cryptographic chaining, external WORM storage) is what makes audit trails forensically useful when it matters. | ☐ |
| 7 | Failure modes default to deny — fail-safe is verified through chaos testing, not assumed ‖ "We fail safely" is a hope until it is exercised. Chaos engineering, security game days, and explicit failure-mode tests turn the assumption into evidence. The first time fail-safe is tested should not be during an incident. | ☐ |
| 8 | Certificate lifecycle is fully automated — issuance, rotation, revocation, all without manual steps ‖ Manual cert renewals are a category of latent incident: the renewal email gets missed, the cert expires on a Friday, the on-call engineer is paged, and the whole production system needs an emergency fix. Automation eliminates the category. | ☐ |
| 9 | Vulnerability scanning runs on every dependency change with SLOs for fix time by severity ‖ Discovering vulnerabilities is the cheap part; fixing them is where most programmes break down. SLOs for fix time per severity convert "we should patch that" into actionable, measurable work that gets prioritised against other engineering. | ☐ |
| 10 | Incident response procedures are exercised regularly — tabletop or live drills, not first run during the real incident ‖ A response procedure that has never been exercised is fiction. Quarterly tabletops, annual live drills, and periodic chaos exercises keep the procedures honest and the team capable. The cost of practice is much less than the cost of finding out during the real event that the runbook is wrong. | ☐ |

---

## Related

[`principles/foundational`](../../principles/foundational) | [`principles/domain-specific`](../../principles/domain-specific) | [`principles/cloud-native`](../../principles/cloud-native) | [`patterns/data`](../data) | [`patterns/deployment`](../deployment) | [`patterns/integration`](../integration)

---

## References

1. [OWASP Top 10](https://owasp.org/Top10/) — *owasp.org*
2. [NIST Cybersecurity Framework (CSF)](https://www.nist.gov/cyberframework) — *nist.gov*
3. [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — *NIST*
4. [Adam Shostack — Threat Modeling: Designing for Security](https://shostack.org/books/threat-modeling-book) — *shostack.org*
5. [STRIDE Threat Model](https://en.wikipedia.org/wiki/STRIDE_model) — *Wikipedia*
6. [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/) — *owasp.org*
7. [CIS Controls](https://www.cisecurity.org/controls) — *cisecurity.org*
8. [Latacora — Cryptographic Right Answers](https://www.latacora.com/blog/2018/04/03/cryptographic-right-answers/) — *latacora.com*
9. [Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege) — *Wikipedia*
10. [Defense in Depth (computing)](https://en.wikipedia.org/wiki/Defense_in_depth_%28computing%29) — *Wikipedia*
