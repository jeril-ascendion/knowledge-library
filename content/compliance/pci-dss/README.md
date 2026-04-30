# PCI DSS

The strategic guide for Payment Card Industry Data Security Standard compliance posture — recognising that the team's cardholder-data-environment scope drawn deliberately to minimise the systems in scope rather than expanded by accident through unmanaged data flows that pull adjacent systems into scope, the network-segmentation architecture that validates segmentation effectiveness through quarterly testing rather than relies on segmentation existing in network diagrams alone, the data-flow inventory for primary account number values that traces every storage, processing, and transmission path explicitly rather than discovers paths during audit, the encryption-key-management architecture that satisfies PCI DSS Requirement 3.5 and 3.6 with documented key custodian roles rather than platform-default key configurations, the compensating-control discipline that justifies deviations from the standard requirements with explicit risk analysis rather than ad-hoc exception processes, and the budget-violation interpretation that treats every PCI Report on Compliance finding as architectural signal rather than as administrative defect to remediate are what determine whether the team's payment-card-data posture genuinely protects the cardholder data the standard exists to protect or whether the institution holds compliant certification while operating with cardholder-data exposure that the limited audit scope did not surface.

**Section:** `compliance/` | **Subsection:** `pci-dss/`
**Alignment:** PCI DSS v4.0.1 | PCI DSS Glossary | PCI Council Self-Assessment Questionnaires | PCI Council Designated Entities Supplemental Validation | EMV / 3DS related standards
---

## What "PCI DSS compliance" means — and how it differs from generic application security

A *primitive* approach to PCI DSS is to engage a Qualified Security Assessor before the annual assessment deadline, walk through the requirement-by-requirement checklist, produce evidence for each requirement at audit time, achieve attestation, and treat PCI DSS as something that re-activates twelve months later. Between assessments, scope creeps invisibly as new integrations introduce paths for cardholder data the institution did not anticipate; segmentation drifts as network changes propagate; key rotations slip past their cadences; the next assessment finds gaps that were not gaps at last year's assessment because the underlying architecture has shifted in the intervening year.

The *architectural* alternative is to recognise that PCI DSS is *engineering specification* expressed as a control standard. The 12 high-level requirements decompose into specific testable controls; the controls operate continuously; the cardholder-data-environment scope is an architectural artefact maintained in the engineering process rather than re-discovered at audit time; the segmentation architecture is validated quarterly; the data-flow inventory is updated when integrations change; the key-management architecture is operated with named roles and documented procedures. The annual Report on Compliance is the periodic external verification of the continuous discipline, not a substitute for it.

This is *not* the same as generic application security — many security-competent organisations protect customer data well without holding payment-card data and without being subject to PCI DSS. PCI DSS's added value is the *prescriptive specificity* about cardholder data: explicit storage prohibitions on Sensitive Authentication Data, explicit retention limits, explicit cryptographic requirements on PAN, explicit logging requirements, and explicit segmentation expectations. The prescriptions are tighter than most generic security baselines because the regulated data class is uniquely valuable to attackers and uniquely portable.

This is also *not* the same as the [BSP & AFASA](../bsp-afasa), [GDPR](../gdpr), or [ISO 27001](../iso27001) compliance pages. PCI DSS is *industry-mandatory* through the card-brand contracts rather than statutory, applies to entities that store, process, or transmit cardholder data regardless of jurisdiction, and operates at a different altitude than any of those regimes. An institution may simultaneously be subject to PCI DSS (because it accepts cards) and to BSP supervision (because it is a Philippine FSI) and to GDPR (because it serves EU residents) and certified to ISO 27001 (as a voluntary management-system framework); the architectural patterns must satisfy all four rather than treating them as alternatives.

The architectural signature of well-specified PCI DSS compliance is *bounded scope with verified boundaries*. The cardholder-data environment is drawn deliberately small; the boundary is enforced by architectural patterns (network segmentation, application-layer separation, identity-and-access boundaries); the boundary is tested quarterly; data flows that would expand scope are identified at design time and either blocked or accepted with explicit scope expansion. When the QSA examines the environment, the boundary is producible. When the boundary has drifted, the QSA finds it before the institution does — and the post-audit remediation is more expensive than the architectural discipline that would have prevented the drift.

## Six principles

### 1. Draw cardholder-data-environment scope deliberately and minimise it through architecture
The CDE is the set of systems that store, process, or transmit cardholder data, plus systems connected to or that could affect the security of those systems. Scope expands silently through unmanaged data flows: a marketing analytics integration that receives anonymised transaction data without realising the dataset includes truncated PANs in a metadata field; a fraud-prevention service that receives full PANs to build behavioural models; a logging pipeline that captures HTTP request bodies including form-submitted card data. Each invisible expansion drags the receiving system into scope and multiplies the assessment burden.

The discipline is to draw the CDE deliberately and use architectural patterns to minimise it: tokenisation early in the payment flow (replacing PAN with a token before downstream systems see it), point-to-point encryption (encrypting card data at the point of capture so intermediate systems handle ciphertext only), payment-iframe approaches (outsourcing the card-capture surface entirely to a PCI-compliant payment service provider), and explicit data-flow review for any integration that touches the payment path.

#### Architectural implications
Minimised scope produces dramatically lower compliance cost because fewer systems require the PCI DSS control set. The trade-off is that minimisation requires architectural investment upfront — tokenisation services, P2PE-validated terminals, payment service provider integrations — that pay back only at audit time. The institution that under-invests in scope minimisation pays at every audit and at every architectural change that touches the CDE.

#### Quick test
For your CDE, list the systems in scope. Compare to a freshly-drawn data-flow diagram tracing PAN from capture through processing to settlement. Are there in-scope systems not on the list, or out-of-scope systems that touch PAN? If either, the scope is inaccurate and the compliance posture is operating on incorrect boundary information.

### 2. Validate segmentation effectiveness through quarterly testing, not through diagram review
PCI DSS Requirement 11.4.5 obligates segmented entities to verify segmentation effectiveness through penetration testing at least every twelve months, and Designated Entities Supplemental Validation requires more frequent verification for higher-volume entities. The intent is that segmentation is not a property of network diagrams; it is a property of network behaviour under test. Diagrams describe intent; tests verify reality. The two diverge over time as network changes propagate without the diagram-update discipline keeping pace.

The discipline is the segmentation-test programme: periodic attempted lateral movement from out-of-scope segments to in-scope segments; periodic verification that out-of-scope systems cannot reach in-scope systems on payment-relevant ports; documented test plans, results, and corrective actions for any segment penetration. The cadence is matched to the rate of network change rather than just the regulatory minimum; entities with frequent changes test more often, entities with stable infrastructure test at the regulatory floor.

#### Architectural implications
Segmentation-test results feed back into the network architecture. Penetrable segments either get architectural hardening (firewall rule changes, microsegmentation, identity-aware proxies) or get reclassified into the CDE — either response is valid; the wrong response is to hand-wave the test result and not address it. The test programme makes the architecture honest about whether segmentation is real or aspirational.

#### Quick test
For your last segmentation test, what was the scope, what was the methodology, what gaps were found, and how were they remediated? If the answer is "we run penetration tests annually and they came back clean," the test scope may not include cross-segment lateral-movement attempts that segmentation tests specifically require.

### 3. Maintain a PAN data-flow inventory that traces every storage, processing, and transmission path
The PCI DSS Reporting Instructions and the Cardholder Data Discovery requirements obligate the institution to know where PAN is stored, processed, and transmitted. Many entities discover at assessment time that PAN is present in places they did not catalogue — backup files, support-ticket attachments, debugging logs, email screenshots, customer-service call recordings — and the assessor's discovery becomes a finding rather than the institution's prior knowledge becoming an architectural plan.

The discipline is the PAN data-flow inventory as a continuously-maintained artefact. New integrations are reviewed for PAN paths before deployment; logs and traces are reviewed for inadvertent PAN capture; backup pipelines are reviewed for PAN propagation; legacy data stores are scanned for PAN that should have been deleted under retention rules. The inventory is the input to the scope determination and to the data-deletion programme.

#### Architectural implications
The PAN inventory drives architectural patterns that reduce its volume. Once the institution sees how PAN flows through its systems, it identifies the points where tokenisation can replace PAN, where retention can be tightened, and where encryption-in-transit can be hardened. The inventory is not just a compliance artefact; it is the input to the architectural improvements that progressively reduce CDE scope.

#### Quick test
Run a discovery scan against your non-CDE storage. Does any PAN appear? If yes, those storage locations are either silent CDE additions or storage that was supposed to have deleted the data and did not. Either is architectural debt.

### 4. Operate encryption-key-management with named custodian roles and documented procedures
PCI DSS Requirements 3.5 and 3.6 specify obligations on cryptographic-key management: documented policies for key generation, distribution, storage, access controls, retirement, and replacement; key-encrypting keys distinct from data-encrypting keys; key custodians with named responsibilities; split-knowledge and dual-control where keys are managed manually. Cloud-platform default key-management may not satisfy all of these obligations, particularly the split-knowledge and dual-control aspects, and the institution must architect the key-management posture rather than rely on platform defaults.

The discipline is the key-management-architecture document: which keys exist, how they are generated, where they are stored, who has access, what rotation cadence applies, what evidence is captured at each lifecycle event. Key custodian roles are filled by named individuals; their responsibilities are documented; their access is logged; their training is current.

#### Architectural implications
Key-management architecture drives concrete platform choices. AWS KMS with HSM-backed keys, Azure Key Vault with managed HSMs, on-premises HSMs with cloud applications using customer-managed keys — each is a valid architectural pattern with different operational characteristics. The choice ripples into application design (when keys are retrieved, how rotation is handled gracefully, how compromise is responded to) and into operational practice (custodian training, key-ceremony procedures, audit-evidence capture).

#### Quick test
Name the key custodians for the encryption keys protecting PAN at rest in your CDE. If the answer is "the cloud provider manages it," the institution has delegated rather than retained the responsibility, and the assessor will want to see the contractual basis for that delegation in the cloud-provider arrangement.

### 5. Use compensating controls deliberately with explicit risk analysis, not as routine workaround
PCI DSS allows compensating controls when the institution cannot meet a stated requirement due to legitimate technical or documented business constraint. The compensating control must satisfy the original intent of the requirement, provide a similar level of defence, be above-and-beyond other PCI DSS requirements, and be commensurate with the risk imposed by the unmet requirement. Each compensating control is documented in a Compensating Control Worksheet attached to the Report on Compliance.

The risk in compensating-control practice is using them as routine workarounds for requirements the institution prefers not to implement. Each compensating control adds operational complexity, requires its own evidence trail, and is scrutinised by the assessor each cycle. A clean compliance posture has few compensating controls; a stretched compliance posture has many. The architectural discipline is to either implement the requirement properly or document the compensating control with the rigour the worksheet demands — including the explicit risk analysis showing why the compensating control is genuinely equivalent.

#### Architectural implications
Compensating controls represent architectural debt by definition: the institution is meeting the standard's intent through indirect means rather than directly. Each compensating control should have a remediation timeline pointing to when the direct implementation will replace it, just as security suppression-ledger entries have review dates. Without the timeline, compensating controls accumulate indefinitely and the assessment cost grows.

#### Quick test
List the compensating controls in your most-recent Report on Compliance. For each, what is the remediation timeline? If the timeline is "indefinite" or unrecorded, the compensating control is functioning as a permanent architectural compromise rather than as a temporary bridge.

### 6. Treat every Report on Compliance finding and self-assessment gap as architectural signal
External QSA findings, internal self-assessment observations, vulnerability-scan failures, segmentation-test gaps — each is information about where the architecture has drifted from the standard's intent. The architectural response mirrors the cross-cutting NFR debt-ledger pattern: every finding gets a recorded decision (close / accept / revise), an owner, a remediation timeline, and a trajectory tracked across assessment cycles.

The discipline is the PCI-finding ledger as a first-class artefact. Findings are catalogued by requirement, by assessment cycle, by remediation status; trajectory across cycles is visible at architectural altitude rather than only inside the compliance team. Cross-cutting finding patterns (the same requirement failing in multiple cycles) trigger architectural review rather than incremental remediation.

#### Architectural implications
The trajectory of findings is the empirical validation that the compliance architecture is improving rather than oscillating with audit-window activity. The same cross-cutting NFR pattern as maintainability suppression ledger, security finding ledger, reliability burn-rate review, usability finding ledger, BSP & AFASA regulatory-finding ledger, GDPR finding ledger, and ISO 27001 ISMS-finding ledger. The shape is the same; the domain is different.

#### Quick test
For findings from the last three Reports on Compliance, are decisions and trajectory visible at architectural altitude? Or are findings closed within the compliance team without architectural review? The latter loses the trajectory signal and architectural review cannot run.

## Five pitfalls

### ⚠️ Allowing CDE scope to expand silently through unmanaged integrations
New integrations that touch the payment path or capture PAN drag systems into scope without the institution noticing until the next assessment. The fix is the design-review gate that examines integrations for PAN paths and either blocks the expansion or explicitly accepts the scope addition.

### ⚠️ Treating segmentation as a property of network diagrams rather than network behaviour
Diagrams describe intent; behaviour is what the assessor tests. The fix is the quarterly segmentation-effectiveness test programme with documented methodology, results, and corrective actions feeding back into network architecture.

### ⚠️ Discovering PAN at audit time in storage locations the institution did not catalogue
Inadvertent PAN capture in logs, backups, support tickets, and call recordings is a frequent assessment finding. The fix is the continuously-maintained PAN data-flow inventory plus periodic discovery scans against non-CDE storage.

### ⚠️ Relying on platform default key-management to satisfy Requirements 3.5 and 3.6
Cloud platform defaults may not implement all of the obligations on key custodian roles, split knowledge, and dual control that the standard requires. The fix is the explicit key-management-architecture document with named roles, documented procedures, and evidence captured at each lifecycle event.

### ⚠️ Using compensating controls as routine workarounds rather than as documented bridges
Each compensating control adds operational complexity and assessment cost; accumulating them indefinitely produces a fragile compliance posture. The fix is the explicit remediation timeline per compensating control, treating each as architectural debt with a planned payoff date.

## PCI DSS compliance architecture checklist

| # | Check | Status |
|---|---|---|
| 1 | Cardholder-data-environment scope is documented with deliberate boundary decisions | ☐ |
| 2 | PAN data-flow inventory traces all storage, processing, and transmission paths | ☐ |
| 3 | Segmentation-effectiveness testing runs quarterly with documented methodology | ☐ |
| 4 | Tokenisation, P2PE, or payment-iframe patterns are applied to minimise scope | ☐ |
| 5 | Encryption-key-management architecture document names custodians and procedures | ☐ |
| 6 | Key rotation cadences are scheduled and evidence is captured per rotation | ☐ |
| 7 | Compensating controls have remediation timelines with named direct-implementation targets | ☐ |
| 8 | Sensitive Authentication Data storage prohibitions are enforced architecturally | ☐ |
| 9 | Quarterly vulnerability scans cover all in-scope systems with remediation tracking | ☐ |
| 10 | PCI-finding ledger records decision (close / accept / revise) per finding with trajectory | ☐ |

## Related

- [BSP & AFASA](../bsp-afasa) — sister page on Philippine FSI regulation that may apply alongside PCI DSS
- [GDPR](../gdpr) — sister page on EU data-protection regime where cardholder data is also personal data
- [ISO 27001](../iso27001) — sister page on information-security management system frameworks
- [Security NFRs](../../nfr/security) — observable security requirements that PCI controls implement
- [Reliability NFRs](../../nfr/reliability) — availability obligations affecting in-scope payment systems
- [Application Security](../../security/application-security) — patterns implementing many PCI requirements
- [Cloud Security](../../security/cloud-security) — patterns governing cloud-deployed CDE components
- [Encryption](../../security/encryption) — patterns supporting Requirements 3.5 and 3.6
- [Authentication & Authorization](../../security/authentication-authorization) — implements PCI access controls
- [Vulnerability Management](../../security/vulnerability-management) — supports quarterly scan obligations
- [Templates: ADR Template](../../templates/adr-template) — how scope and compensating-control decisions are recorded

## References

1. [PCI Security Standards Council](https://www.pcisecuritystandards.org/) — *pcisecuritystandards.org*
2. [PCI DSS Document Library](https://www.pcisecuritystandards.org/document_library/) — *pcisecuritystandards.org*
3. [PCI DSS (Wikipedia overview)](https://en.wikipedia.org/wiki/Payment_Card_Industry_Data_Security_Standard) — *en.wikipedia.org*
4. [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/) — *owasp.org*
5. [OWASP Top 10](https://owasp.org/www-project-top-ten/) — *owasp.org*
6. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) — *nist.gov*
7. [ISO 27001](https://www.iso.org/standard/27001) — *iso.org*
8. [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html) — *aws.amazon.com*
9. [EMVCo](https://www.emvco.com/) — *emvco.com*
10. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
