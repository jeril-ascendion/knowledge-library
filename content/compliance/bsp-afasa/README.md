# BSP & AFASA (Philippine FSI)

The strategic guide for Bangko Sentral ng Pilipinas regulation and the Anti-Financial Account Scamming Act compliance posture in Philippine financial services — recognising that the team's BSP-supervised-institution status governs which circulars apply to which workloads rather than blanket-application of every published circular, the AFASA verification-and-victim-protection obligations require concrete architectural patterns for account-takeover detection and reporting rather than after-the-fact policy statements, the layered regulatory cadence operates at multiple frequencies (annual ICAAP submission, quarterly capital-adequacy reporting, monthly liquidity reporting, twenty-four-hour incident notification, two-hour disruption notification) rather than a single annual cycle, the inter-regulator coordination between BSP and the Anti-Money Laundering Council and the Insurance Commission and the Securities and Exchange Commission demands explicit architectural treatment of cross-regulator data sharing, the Philippine-specific data-residency obligations imposed by the Data Privacy Act and BSP regulations on cloud-service-provider arrangements require concrete jurisdictional architecture rather than generic global patterns, and the budget-violation interpretation that treats every regulatory finding as architectural signal rather than as administrative defect to remediate are what determine whether the team's compliance posture is genuinely calibrated against the supervised-institution category and the threats the AFASA was passed to address or whether the institution operates in nominal compliance while remaining vulnerable to the specific risks that drove the regulatory framework into existence.

**Section:** `compliance/` | **Subsection:** `bsp-afasa/`
**Alignment:** Bangko Sentral ng Pilipinas Manual of Regulations for Banks (MORB) | BSP Circular 982 (IT Risk Management) | BSP Circular 1140 (AFASA implementation) | Anti-Financial Account Scamming Act (Republic Act 12010) | Data Privacy Act of 2012 (Republic Act 10173)
---

## What "BSP & AFASA compliance" means — and how it differs from generic banking-security posture

A *primitive* approach to Philippine FSI compliance is to treat the BSP regulatory framework as a checklist to satisfy at examination time, apply globally-published banking-security baselines to every workload uniformly, treat AFASA as another fraud-rule layer added to the existing fraud system, and assume the institution is compliant if no findings emerged from the most recent BSP examination. Six months later, an account-takeover incident triggers AFASA reporting obligations the institution did not realise applied; the response is delayed because the runbook was written against generic incident-response patterns rather than the specific 24-hour and 2-hour notification windows AFASA mandates; the BSP issues a memorandum of understanding specifying remedial actions; the institution adds another checklist to the compliance binder and the cycle continues.

The *architectural* alternative is to recognise that the BSP framework is *jurisdictionally specific* — it embeds Philippine-context choices about supervised-institution categories, financial-system protection priorities, AML-CFT integration, and customer-protection obligations that diverge from Basel-III-only or US-FFIEC-only regulatory baselines. AFASA is *architecturally specific* — it specifies notification timelines, victim-protection patterns, account-freezing mechanics, and inter-bank coordination protocols that change what an incident-response architecture actually has to produce. Compliance with both is not a binder; it is a set of architectural patterns each traceable to a specific circular or statutory provision, each measurable against the obligations they implement, each updated when BSP issues a new circular or amends an existing one.

This is *not* the same as the [security architecture pages](../../security) — those cover the design patterns and platform choices that implement security controls. This page covers the *jurisdictional regulatory specifications* that those patterns must satisfy in the Philippine FSI context. Security architecture answers "how do we build it"; BSP & AFASA compliance answers "what specific Philippine regulatory obligations must our build observably meet, traced to which circular or statute."

This is also *not* the same as the [GDPR](../gdpr), [ISO 27001](../iso27001), or [PCI DSS](../pci-dss) compliance pages — those cover other regulatory regimes whose obligations may apply to Philippine FSI institutions in addition to BSP & AFASA but whose design intent and scope differ substantially. A Philippine bank handling EU-resident data must comply with both BSP regulations (jurisdictional supervisor) and GDPR (extraterritorial data-protection regime); the two regimes overlap in some areas and diverge in others, and the architectural patterns must satisfy both rather than picking one.

The architectural signature of well-specified BSP & AFASA compliance is *traceable jurisdictional alignment*. Each control in the system points to a specific circular, memorandum, or statutory provision; the institution-category-to-circular mapping is documented; the multi-frequency reporting cadences are instrumented; the AFASA notification mechanics are exercised through periodic drills. When a new circular issues, the impact-assessment process identifies which existing controls satisfy it, which need modification, and which need new architectural patterns — the practice is calibrated to the regulatory rhythm rather than reactive to examination findings.

## Six principles

### 1. Map institution category to the applicable circular set rather than applying every circular uniformly
The BSP supervises a heterogeneous population of institutions: universal banks, commercial banks, thrift banks, rural banks, electronic money issuers, virtual-asset service providers, payment system operators, and trust corporations. Each category has a different applicable circular set; some circulars apply across all supervised institutions, others apply only to specific categories. A digital bank does not inherit every circular written for a universal bank; an EMI does not have the same capital-adequacy obligations as a thrift bank. Treating every circular as universally applicable produces a compliance programme that is partly correct and substantially over-engineered, with the cost being that the genuinely critical circulars get less architectural attention because the team is treating everything as equally important.

The discipline is to maintain the explicit institution-category-to-circular mapping as an architectural artefact: this institution operates in category X under MORB; the circulars applicable to category X are A, B, C; circulars D, E, F apply to category Y but not X; the rationale for each inclusion or exclusion is documented. The mapping is reviewed when BSP issues amendments and when the institution's licence status changes.

#### Architectural implications
The mapping drives the internal compliance baseline. Controls implemented to satisfy circulars not actually applicable to the institution waste investment; controls missing for circulars that do apply create regulatory exposure. The mapping is the input to the impact-assessment process when new circulars issue: which category does the new circular target, does our institution fall in that category, what are the compliance-programme deltas.

#### Quick test
Ask the compliance practice "which BSP circulars apply to our institution and on what basis?" If the answer is "we follow the MORB and applicable circulars," the mapping is implicit. If the answer names the specific category and lists the circulars by number with rationale, the mapping is explicit and the architectural baseline is grounded.

### 2. Treat AFASA notification timelines as architectural commitments, not as procedural appendices
The Anti-Financial Account Scamming Act and BSP Circular 1140 specify notification timelines that are unforgiving by design: institutions must notify the BSP within twenty-four hours of becoming aware of a financial account scam incident affecting their customers, and must notify the BSP within two hours of a material disruption to financial services. These timelines are not procedural niceties; they are architectural requirements. A system that detects an incident at 03:00 and produces the BSP notification at 11:00 has missed the two-hour window if the incident qualified as a service-disruption event. The architecture that makes the notification dependable is not the runbook; it is the detection-to-notification pipeline whose latency budget includes the human-decision time and which is exercised at game-day cadence.

The discipline is to specify the notification-pipeline NFRs at the same rigour applied to user-facing performance NFRs: detection-to-classification time, classification-to-notification-draft time, draft-to-submission time, with budgets that fit inside the regulatory window. The pipeline is exercised through quarterly drills that produce evidence; the drill-to-actual variance is itself a compliance signal.

#### Architectural implications
The notification pipeline drives concrete architectural choices: classification rules cannot be in a manual-review queue; notification templates must be pre-approved with the regulator's required fields; the institution's authorised signatories must be identified in advance with on-call rotation. Each of these is engineering work, and it is engineering work whose budget is set by the regulatory clock rather than by the institution's preferred operating cadence.

#### Quick test
For the AFASA two-hour disruption notification window, what is the documented detection-to-submission budget for each pipeline stage, and what is the actual measured time from the most recent drill? If neither exists, the institution is hoping the obligation will not need to be exercised in production rather than engineering for the case where it does.

### 3. Architect for the multi-frequency reporting cadence rather than a single annual rhythm
BSP supervision operates at multiple frequencies simultaneously. Annual: Internal Capital Adequacy Assessment Process (ICAAP) submission, comprehensive examination, related-party-transactions disclosure. Quarterly: capital-adequacy ratio reporting, financial-soundness indicators, large-exposures reporting. Monthly: liquidity coverage ratio, balance-sheet snapshot, anti-money-laundering transaction reporting. Continuous: real-time RTGS settlement monitoring, ATM-network availability, suspicious-transaction-report submission within the prescribed window. A compliance architecture optimised only for the annual cycle misses the higher-frequency obligations; one optimised only for the highest frequency over-engineers the slower ones.

The discipline is the multi-frequency calendar artefact: what report is due at what cadence, with what data inputs, produced by which workload, validated by which control. The calendar drives the ETL schedule, the data-quality SLAs on inputs, and the human-review windows. Cadences that share inputs are designed once and consumed multiply; cadences with unique inputs are individually scoped.

#### Architectural implications
The multi-frequency cadence drives the data-platform architecture. Monthly liquidity reporting cannot wait for an annual data-warehouse refresh; quarterly capital reporting cannot tolerate stale data inputs; the two-hour disruption notification is a real-time obligation that bypasses batch processes entirely. The platform's tiering — real-time event stream, near-real-time analytics, batch warehouse — is shaped by the cadence portfolio, not by generic data-architecture preferences.

#### Quick test
Examine your reporting calendar. Is each periodic obligation listed with cadence, due date, data-input dependencies, owning workload, and data-quality target? Or is the calendar a list of report names without the production architecture documented? The latter produces compliance that works most months and fails when one of the dependencies is unavailable on the due date.

### 4. Document inter-regulator coordination as explicit architectural surfaces
Philippine FSI institutions operate under multiple regulators whose jurisdictions overlap. BSP supervises banking and quasi-banking activities. The Anti-Money Laundering Council supervises AML-CFT compliance. The Insurance Commission supervises insurance products. The Securities and Exchange Commission supervises capital-markets activity. The National Privacy Commission supervises personal-data processing under the Data Privacy Act. A retail bank may report to all five regulators on different obligations, and the regulators occasionally require inter-regulator data sharing or coordinated examinations. Treating each regulator as a separate compliance silo produces duplicated controls, inconsistent definitions across reports, and inability to respond coherently to coordinated examinations.

The discipline is to document the inter-regulator architectural surfaces: which data flows to which regulator, which controls satisfy multiple regulators simultaneously, which definitions are normalised across reports versus regulator-specific. The surfaces are themselves architectural artefacts subject to review when regulator MOUs change or when the institution's product mix shifts the regulatory perimeter.

#### Architectural implications
Inter-regulator architecture drives the data-governance posture. A customer record reported to BSP for AML must use the same identity definitions as the record reported to the AMLC for STR purposes; if they diverge, the institution has two truths about the same customer and either reconciliation cost rises or one regulator is receiving inaccurate data. The shared-definitions discipline is itself a compliance architecture decision, recorded as an ADR.

#### Quick test
For your top three regulatory reports, identify the customer-identifier field, the transaction-amount field, and the date-of-event field. Are the definitions identical across the three reports? If they diverge, the reports cannot be reconciled and the institution is at risk of inconsistent regulatory disclosure.

### 5. Specify Philippine data-residency requirements as architectural contracts on cloud and third-party arrangements
BSP regulations (notably Circular 982) and the Data Privacy Act impose specific obligations on outsourcing arrangements, cross-border data transfers, and cloud-service-provider relationships. The obligations include: pre-arrangement notification or approval, ongoing supervisory access to outsourced functions, data-localisation requirements for specified data classes, exit-and-portability provisions in service agreements, and the institution's continuing accountability for outsourced activities. A cloud architecture that treats the cloud provider as a generic platform — without explicit data-residency configuration, without supervisory-access provisions, without exit-portability planning — fails these obligations regardless of how secure the platform is in absolute terms.

The discipline is the explicit cloud-and-third-party architecture document: which workloads can be deployed in which regions, which third parties hold which data classes, how supervisory access is provisioned, what the exit-and-portability plan looks like for each major provider. The document is reviewed at provider-onboarding, at provider-renewal, and when BSP issues amended outsourcing guidance.

#### Architectural implications
Data-residency requirements drive concrete cloud-region selection and configuration: workloads handling regulated customer data deployed to Manila or Singapore regions with explicit data-localisation flags; backup and disaster-recovery topology constrained to remain within the regulator-approved geography; key-management services configured so encryption keys do not leave the prescribed jurisdiction. None of this is implicit in the cloud provider's default configuration; all of it is engineering work driven by the regulatory contract.

#### Quick test
For your most-recent cloud-provider workload, name the BSP outsourcing notification or approval that was filed, the data-residency configuration applied, and the exit-and-portability plan documented. If any is missing, the workload may be operating without the regulatory architecture the circular requires.

### 6. Treat every regulatory finding and circular issuance as architectural signal, not as administrative event
A BSP examination finding, a memorandum of understanding requiring remediation, a newly issued circular — each is information about where the institution's compliance architecture must change. The architectural response is to treat the finding the same way the maintainability suppression-ledger treats new violations and the security finding-ledger treats audit observations: with a recorded decision (close / accept / revise), an owner, a timeline, and a trajectory tracked across cycles. The aggregate of regulatory-finding decisions is itself a compliance-posture signal; rising finding rates indicate the architecture is diverging from regulatory expectations even if individual findings are addressed.

The discipline is the regulatory-finding ledger as a first-class compliance artefact. Findings are catalogued by circular, by examination cycle, by remediation status; trajectory across cycles is visible at architectural altitude rather than only inside the compliance team; cross-cutting finding patterns (the same control failing in multiple examinations) trigger architectural review rather than incremental patching.

#### Architectural implications
The finding ledger is the cross-cutting NFR pattern again: every well-run compliance domain produces a debt-ledger artefact whose movement is architectural signal. Maintainability has the suppression ledger, security has the finding ledger, reliability has the burn-rate review, usability has the usability-finding ledger, and BSP & AFASA compliance has the regulatory-finding ledger. The shape is the same; the domain is different.

#### Quick test
For findings from your last BSP examination, does each have a recorded decision (close / accept / revise) with owner and date, and is the trajectory across the last four examination cycles visible? If findings are closed silently as the compliance team addresses them in routine work, the trajectory signal is lost and architectural review cannot run.

## Five pitfalls

### ⚠️ Treating every BSP circular as applicable rather than mapping by institution category
The MORB and the BSP circular series collectively run to thousands of pages; not all of it applies to every institution. Treating it uniformly wastes investment on irrelevant controls and dilutes attention on the genuinely critical ones. The fix is the institution-category-to-circular mapping with explicit inclusions, exclusions, and rationale per item.

### ⚠️ Treating AFASA notification timelines as procedural rather than architectural
The two-hour and twenty-four-hour windows are unforgiving. A detection-to-notification pipeline that is not engineered to fit inside those windows will miss them under stress. The fix is to specify the pipeline's stage budgets, instrument the actual stage latencies, exercise the pipeline through quarterly drills, and use drill-to-actual variance as a compliance signal.

### ⚠️ Optimising the compliance architecture for the annual examination cycle only
Annual cycles are visible and ritualised; quarterly, monthly, and real-time obligations operate quietly underneath and fail in ways that are not detected until the next examination. The fix is the multi-frequency calendar with each cadence having its own owning workload, data-quality target, and validation discipline.

### ⚠️ Treating each regulator as a separate compliance silo
BSP, AMLC, IC, SEC, and NPC regulate overlapping aspects of the institution; treating them as silos produces inconsistent definitions, duplicated controls, and incoherent responses to coordinated examinations. The fix is to identify the inter-regulator architectural surfaces, normalise shared definitions, and document which controls satisfy multiple regulators simultaneously.

### ⚠️ Cloud and third-party arrangements without explicit BSP outsourcing architecture
Cloud providers' default configurations do not satisfy BSP outsourcing obligations on data residency, supervisory access, and exit-and-portability. Workloads deployed without explicit treatment of these obligations operate in regulatory exposure regardless of platform security. The fix is the explicit cloud-and-third-party architecture document with per-arrangement configuration, notifications, and exit planning.

## BSP & AFASA compliance architecture checklist

| # | Check | Status |
|---|---|---|
| 1 | Institution category is documented with applicable BSP circular set | ☐ |
| 2 | Each applicable circular is traced to specific architectural controls | ☐ |
| 3 | AFASA notification pipeline NFRs are specified with stage budgets | ☐ |
| 4 | AFASA notification drills run on quarterly cadence with recorded variance | ☐ |
| 5 | Multi-frequency reporting calendar is published with owning workloads | ☐ |
| 6 | Inter-regulator data-flow surfaces are documented with shared definitions | ☐ |
| 7 | Cloud-provider arrangements have BSP outsourcing notification on file | ☐ |
| 8 | Data-residency configuration is applied per regulated data class | ☐ |
| 9 | Exit-and-portability plan exists for each major third-party provider | ☐ |
| 10 | Regulatory-finding ledger records decision (close / accept / revise) per finding | ☐ |

## Related

- [GDPR](../gdpr) — sister page on EU data-protection regime that may apply extraterritorially
- [ISO 27001](../iso27001) — sister page on information-security management system frameworks
- [PCI DSS](../pci-dss) — sister page on payment-card-data handling regimes
- [Security NFRs](../../nfr/security) — observable security requirements that compliance controls implement
- [Reliability NFRs](../../nfr/reliability) — availability obligations affecting AFASA disruption-notification triggers
- [Application Security](../../security/application-security) — patterns implementing many of the controls referenced
- [Cloud Security](../../security/cloud-security) — patterns governing cloud-region selection and key-management
- [Authentication & Authorization](../../security/authentication-authorization) — patterns supporting account-takeover detection
- [Vulnerability Management](../../security/vulnerability-management) — operational practice feeding finding-ledger trajectory
- [Templates: ADR Template](../../templates/adr-template) — how regulatory-finding decisions are recorded

## References

1. [Bangko Sentral ng Pilipinas — Manual of Regulations for Banks](https://www.bsp.gov.ph/Regulations/MORB/MORB.pdf) — *bsp.gov.ph*
2. [BSP Circular 982 — Information Technology Risk Management](https://www.bsp.gov.ph/Regulations/Issuances/2017/c982.pdf) — *bsp.gov.ph*
3. [BSP Circular 1140 — AFASA Implementation](https://www.bsp.gov.ph/Regulations/Issuances/2024/1140.pdf) — *bsp.gov.ph*
4. [Anti-Financial Account Scamming Act (RA 12010)](https://www.officialgazette.gov.ph/2024/07/20/republic-act-no-12010/) — *officialgazette.gov.ph*
5. [Data Privacy Act of 2012 (RA 10173)](https://www.officialgazette.gov.ph/2012/08/15/republic-act-no-10173/) — *officialgazette.gov.ph*
6. [National Privacy Commission](https://privacy.gov.ph/) — *privacy.gov.ph*
7. [Anti-Money Laundering Council](https://www.amlc.gov.ph/) — *amlc.gov.ph*
8. [ISO 27001](https://www.iso.org/standard/27001) — *iso.org*
9. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) — *nist.gov*
10. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
