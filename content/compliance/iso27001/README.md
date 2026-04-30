# ISO 27001

The strategic guide for ISO 27001 information security management system compliance posture — recognising that the team's risk-driven Statement of Applicability that names which Annex A controls are in scope and which are excluded with rationale rather than treating all 93 controls as mandatorily applicable, the management-system architecture (Plan-Do-Check-Act) that operates as a continuous discipline rather than as a triennial certification ritual, the asset inventory and risk register that drive control selection rather than backwards-justifying control implementations after the fact, the internal-audit programme that runs against the institution's own ISMS rather than rehearsing for the external certification audit, the management-review cadence that produces decisions about programme direction rather than confirming activities already performed, the explicit treatment of the four control themes (organisational, people, physical, technological) at appropriate altitudes rather than treating Annex A as one undifferentiated control list, and the finding-trajectory interpretation that treats audit observations as architectural signal rather than as administrative defects to suppress are what determine whether the team's information-security posture is genuinely calibrated against the threats facing the organisation or whether the institution maintains a certification that satisfies external auditors while operating with the same exposure as before certification.

**Section:** `compliance/` | **Subsection:** `iso27001/`
**Alignment:** ISO/IEC 27001:2022 | ISO/IEC 27002:2022 (controls implementation guidance) | ISO/IEC 27005 (risk management) | NIST Cybersecurity Framework | OWASP SAMM
---

## What "ISO 27001 compliance" means — and how it differs from a generic security programme

A *primitive* approach to ISO 27001 is to engage a consultancy six months before the certification deadline, generate the policy and procedure binder the consultancy templates produce, conduct a stage-1 readiness audit that finds gaps, conduct a stage-2 certification audit that finds fewer gaps, achieve certification, and treat the ISMS as something that re-activates twelve months later for the surveillance audit. Between audits, the binder gathers dust, the policies are not referenced in operational decision-making, and the underlying security posture is whatever the security team would have produced without the ISMS at all. The certification is real; the management system is not.

The *architectural* alternative is to recognise that ISO 27001 is *engineering specification of a management system*. The standard does not specify what controls to implement — it specifies how the institution decides which controls to implement (Clauses 4-10 of the standard) and provides a control catalogue (Annex A) the institution selects from. The selection is justified in the Statement of Applicability with rationale per included and excluded control. The implementation is operated and measured continuously. The internal audit examines the institution's own operation of the ISMS. The management review produces decisions about programme direction. The certification audit examines whether the management system is operating, not whether the institution has memorised the binder.

This is *not* the same as a generic security programme — many organisations operate competent security programmes without ISO 27001 certification. ISO 27001's added value is the discipline of the management system: the explicit risk-to-control traceability, the continuous-improvement cycle, the documented decision rights, and the independent verification through accredited certification. A security programme without that discipline may produce comparable absolute security; the ISMS produces *demonstrable* security under external scrutiny.

This is also *not* the same as the [BSP & AFASA](../bsp-afasa), [GDPR](../gdpr), or [PCI DSS](../pci-dss) compliance pages. ISO 27001 is *cross-jurisdictional and voluntary*; it can satisfy parts of regulatory regimes by providing evidence of management-system discipline, but it does not replace specific regulatory obligations that require regulator-approved frameworks. A bank under BSP supervision benefits from ISO 27001 certification but still must satisfy BSP's specific circulars; a controller subject to GDPR may use ISO 27001 controls as part of demonstrating Article 32 security but still must satisfy the regulation's specific obligations.

The architectural signature of well-specified ISO 27001 compliance is *risk-traceable selectivity*. Every control in the Statement of Applicability traces to specific risks in the risk register; every excluded control has a documented rationale for exclusion; every implemented control has named ownership, operational measurement, and audit evidence. When the management review or external audit examines the ISMS, the trace is producible. When the trace is missing, the institution is in compliance with the certificate but not with the management-system intent.

## Six principles

### 1. Build the Statement of Applicability from the risk register, not from the control list
Annex A of ISO 27001:2022 contains 93 controls organised into four themes (organisational, people, physical, technological). The institution does not implement all 93 mandatorily; it selects which apply based on the risks identified in its risk assessment, documents the selection in the Statement of Applicability, and provides rationale for both inclusions and exclusions. The discipline that distinguishes a real ISMS from a binder is the direction of the work: the SoA flows *from* the risk register *to* the controls, not *from* the control list *to* a back-justified rationale.

The discipline is to run the risk assessment first, identify the threats and vulnerabilities and impacts to the institution's specific information assets, and *then* choose the controls from Annex A that mitigate those risks plus any additional controls outside Annex A that the risk assessment indicates are needed. The SoA documents the selection with traceability: this control is included because it mitigates these risks; this control is excluded because the risk assessment found these risks not applicable to our context.

#### Architectural implications
Risk-driven selection produces a tighter, more focused control set than catalogue-driven selection. The institution implements fewer controls but each control is genuinely tied to a risk. The maintenance cost is lower because controls without operational purpose are excluded explicitly rather than carried as dead weight. The audit defensibility is stronger because the rationale is producible.

#### Quick test
Pick a control from your Statement of Applicability. Ask which risk in the risk register it mitigates. If the answer is "all of them" or "general security," the control was selected catalogue-first. If the answer cites a specific risk-register entry, the selection was risk-driven.

### 2. Operate the management system as continuous Plan-Do-Check-Act, not as triennial certification preparation
The ISMS lifecycle in ISO 27001 follows the Plan-Do-Check-Act cycle. Plan: establish the ISMS, set objectives, perform risk assessment, select controls. Do: implement and operate the controls. Check: monitor effectiveness, conduct internal audits, perform management review. Act: address findings, update the ISMS, refine the controls. The cycle operates continuously; certification is a periodic external verification of the cycle's operation, not a substitute for the cycle.

A common dysfunction is the certification-prep cycle: the institution operates with degraded discipline between audits, then ramps up activity in the months before certification or surveillance audits. The pattern is detectable in evidence trails — most logs show a flurry of activity in the audit-preparation period and quiet in between. The certification auditor sees the activity; the management-system intent is not satisfied.

#### Architectural implications
Continuous operation drives the calendar of ISMS activities. Risk-register reviews on quarterly cadence; internal audits on a rolling annual programme that examines all controls over a three-year cycle; management reviews at consistent cadence with consistent agenda; corrective-action tracking with named owners and timelines. The calendar is itself an architectural artefact; without it, the ISMS degrades to certification-driven episodes.

#### Quick test
Look at your ISMS evidence trail across the past twelve months. Is the activity distributed evenly, or is it concentrated in audit-preparation windows? If concentrated, the management system is operating as ritual rather than as continuous discipline.

### 3. Maintain the asset inventory and risk register as living artefacts that drive control decisions
The asset inventory and risk register are the upstream feeds for the ISMS. They name what the institution is protecting and what it is protecting it from. If they are stale, the controls are mis-targeted; if they are absent, the controls have no documented justification. The discipline is to maintain both as living artefacts: assets are added as new systems come online and removed as systems are decommissioned; risks are added as the threat landscape changes (new attack patterns, new regulatory expectations, new technology adoption changing the attack surface) and re-evaluated as controls mature.

The asset inventory is the join key between the technology architecture and the security architecture. A new system being designed without being entered into the asset inventory is a system whose risks are not assessed, controls are not selected, and audit visibility is absent. The inventory is the architectural integration point that prevents the ISMS and the technology programme from drifting apart.

#### Architectural implications
The asset inventory drives change-management gates. New-system onboarding into the asset inventory becomes a deployment-gate the same way security review and architectural review are deployment-gates. The gate forces the conversation: what is this system, what does it process, what risks does it carry, which controls apply.

#### Quick test
For your most-recent production system addition, was it entered into the asset inventory before deployment, was a risk assessment performed against it, and were the applicable controls identified? If any step is missing, the asset inventory is not gating the work as the ISMS expects.

### 4. Run the internal audit programme on the institution's own ISMS, not on certification rehearsal
ISO 27001 requires internal audits as part of the management system. The audits are *internal*: their purpose is to verify that the ISMS is operating as designed, identify gaps, and feed corrective action. A common dysfunction is to treat the internal audit as a rehearsal for the external certification audit — same scope, same questions, same script. This produces an internal audit that is duplicative with the external audit and adds no diagnostic value beyond what the external audit will already produce.

The discipline is to run internal audits with diagnostic intent: rolling coverage of all controls over the audit cycle, examining controls the external audit does not deeply examine, finding gaps before the external auditor finds them, and producing corrective actions whose closure is verifiable. The internal audit is the institution's mechanism for catching its own drift; outsourcing that mechanism to the external auditor degrades the discipline.

#### Architectural implications
Internal audit independence is itself an architectural decision. Auditors cannot audit work they performed; the audit programme is staffed and scheduled to maintain that independence even within a smaller organisation, including using internal-audit-services vendors where in-house independence is constrained. The independence is provable to the external auditor and is itself an evidence point.

#### Quick test
Look at the most recent internal audit report. Did it find gaps the subsequent external audit also found? Or did it find gaps the external audit did not raise? The first indicates the internal audit is rehearsing; the second indicates it is genuinely catching drift.

### 5. Use the management review to make decisions about ISMS direction, not to confirm activities already performed
ISO 27001 Clause 9.3 specifies inputs to the management review: status of corrective actions, results of audits, performance of controls, risk-environment changes, opportunities for improvement, and others. The output is decisions about ISMS direction: continued resourcing, programme adjustments, scope changes, control modifications. The management review is the institution's strategic decision-point for the ISMS; it is not a status-update meeting.

A common dysfunction is the status-update review where the inputs are presented and the outcome is "noted with thanks." Decisions are not recorded; programme direction does not change as a result of the review; the ritual occurs but the management-control loop is open. The corrective is the explicit-decision discipline: every management review produces named decisions with owners and timelines, recorded in minutes that the next review opens by reviewing.

#### Architectural implications
Management-review decisions are architectural decisions about the ISMS. Treating the review as decision-producing rather than activity-confirming changes the meeting design: pre-circulated inputs, clear decision points named in the agenda, recorded outcomes, follow-up tracking. The discipline mirrors the maturity-guidelines burn-rate-review pattern in [reliability NFRs](../../nfr/reliability) and the security-finding ledger in [security NFRs](../../nfr/security).

#### Quick test
For the most-recent management review, list the decisions made. If the answer is "we noted the status of the controls," the review is not producing the management-control loop the standard requires.

### 6. Treat audit findings and ISMS effectiveness measurements as architectural signal
External audit findings, internal audit findings, control-effectiveness measurements, and risk-register changes — each is information about where the ISMS is performing as designed and where it is drifting. The architectural response mirrors the cross-cutting NFR debt-ledger pattern: every finding gets a recorded decision (close / accept / revise), an owner, and a trajectory tracked across audit cycles. The aggregate is itself an ISMS-posture signal that should be visible at architectural altitude.

The discipline is the ISMS-finding ledger as a first-class artefact, with the same shape as the maintainability suppression ledger, the security finding ledger, the reliability burn-rate review, the usability finding ledger, the BSP & AFASA regulatory-finding ledger, and the GDPR finding ledger. The shape is the same; the domain is different.

#### Architectural implications
Trajectory of findings is the empirical validation that the ISMS is improving rather than oscillating. Rising finding rates trigger architectural review even when individual findings are addressed; recurring findings (the same control failing in multiple audit cycles) trigger root-cause investigation rather than incremental remediation; the trajectory of high-severity findings is the leading indicator that should arrive at management review before it arrives at certification audit.

#### Quick test
Look at audit findings from the past three cycles. Are they trending in the same direction as the institution's risk environment expects? Are findings clustered around specific controls or specific assets? If trajectory analysis is not visible, the management-control loop is open.

## Five pitfalls

### ⚠️ Building the Statement of Applicability from Annex A rather than from the risk register
Catalogue-driven selection produces a control set that is loosely tied to the institution's actual risks and expensive to maintain. The fix is risk-first selection with the SoA documenting the trace from each risk-register entry to the selected control or to the documented exclusion rationale.

### ⚠️ Operating the ISMS as triennial certification preparation rather than continuous discipline
Audit-windowed activity peaks expose that the management system is not operating between audits. The fix is the continuous activity calendar with risk-register reviews, internal audits, management reviews, and corrective-action tracking distributed evenly across the year.

### ⚠️ Allowing the asset inventory and risk register to drift from current operational reality
A stale inventory and register produce a control set targeted at yesterday's environment. The fix is to gate new-system deployments through inventory-update and risk-assessment steps the same way deployments gate through security review and architectural review.

### ⚠️ Running internal audits as rehearsal for external audits rather than as independent diagnostic
Rehearsal duplicates the external audit and finds nothing the external auditor will not also find. The fix is internal audits with diagnostic intent, rolling coverage, independence, and the explicit goal of catching drift before the external auditor catches it.

### ⚠️ Treating the management review as a status-update rather than a decision-making forum
Status-update reviews produce the ritual without the management-control loop. The fix is the explicit-decision discipline: every review produces named decisions with owners and timelines, and the next review opens by reviewing the prior decisions' outcomes.

## ISO 27001 ISMS architecture checklist

| # | Check | Status |
|---|---|---|
| 1 | Risk register is current with named risks per asset and treatment decisions | ☐ |
| 2 | Statement of Applicability traces each control to specific risks or documented exclusion | ☐ |
| 3 | Asset inventory is gated by deployment process and is current | ☐ |
| 4 | ISMS activities are distributed evenly across the year, not concentrated in audit windows | ☐ |
| 5 | Internal audit programme provides rolling coverage of all controls over the cycle | ☐ |
| 6 | Internal auditors are independent of the work they audit | ☐ |
| 7 | Management review minutes record decisions with named owners and timelines | ☐ |
| 8 | Corrective actions from prior reviews are tracked to closure with verifiable evidence | ☐ |
| 9 | Control-effectiveness measurements feed management review inputs | ☐ |
| 10 | ISMS-finding ledger records decision (close / accept / revise) per finding with trajectory | ☐ |

## Related

- [BSP & AFASA](../bsp-afasa) — sister page on Philippine FSI regulation that may run alongside ISMS
- [GDPR](../gdpr) — sister page on EU data-protection regime where ISMS evidence supports Article 32
- [PCI DSS](../pci-dss) — sister page on payment-card-data handling regimes
- [Security NFRs](../../nfr/security) — observable security requirements that ISMS controls implement
- [Maturity Models](../../maturity/models) — including OWASP SAMM as alternative ISMS-style model
- [Application Security](../../security/application-security) — patterns implementing many Annex A controls
- [Cloud Security](../../security/cloud-security) — patterns governing cloud-deployed asset risk
- [Vulnerability Management](../../security/vulnerability-management) — operational practice feeding finding-ledger
- [Authentication & Authorization](../../security/authentication-authorization) — implements identity and access controls
- [Templates: ADR Template](../../templates/adr-template) — how SoA inclusion and exclusion decisions are recorded

## References

1. [ISO 27001](https://www.iso.org/standard/27001) — *iso.org*
2. [ISO 27001 (Wikipedia overview)](https://en.wikipedia.org/wiki/ISO/IEC_27001) — *en.wikipedia.org*
3. [ISO 27002 (controls implementation guidance)](https://www.iso.org/standard/75652.html) — *iso.org*
4. [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) — *nist.gov*
5. [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/) — *owaspsamm.org*
6. [OWASP Top 10](https://owasp.org/www-project-top-ten/) — *owasp.org*
7. [Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) — *en.wikipedia.org*
8. [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html) — *aws.amazon.com*
9. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
10. [Quality Attribute Workshop (SEI)](https://insights.sei.cmu.edu/library/quality-attribute-workshop-third-edition-participants-handbook/) — *sei.cmu.edu*
