# NFR Scorecard

The strategic guide for non-functional requirement scorecards — recognising that the team's per-attribute scoring rather than aggregated quality ratings, the measurable targets specified alongside qualitative levels, the explicit distinction between specified, validated in test, and operating in production, the per-release tracking that shows NFR trajectory rather than single snapshots, the explicit articulation of attribute trade-offs rather than averaged-away tensions, and the captured learnings from validation that update future targets are what determine whether NFRs evolve from architectural assumptions into testable disciplined commitments or whether the system absorbs production NFR violations as inevitable surprises because the scorecard never made the targets concrete enough to validate against.

**Section:** `scorecards/` | **Subsection:** `nfr/`
**Alignment:** ISO/IEC 25010 | CISQ Software Quality Standards | Quality Attribute Workshop (SEI) | Google SRE Workbook | arc42
---

## What "NFR scorecard" means — and how it differs from checklists and ATAM-style trade-off analysis

A *primitive* approach to non-functional requirements is to write them as adjectives in a design document — "the system must be performant, scalable, secure, and highly available" — declare them satisfied by virtue of having said so, and proceed to implementation. After the system enters production and an incident occurs that violates one of the implicit targets, the team performs a post-mortem, identifies what the implicit target was retrospectively, declares it should have been formalised, and adds a sentence to the design document. Subsequent designs inherit the slightly improved adjective list. After eighteen months of incidents, the design document carries thirty NFR adjectives, none of them measurable, and the team genuinely cannot tell from any artefact whether the system meets its NFRs or by how much it misses. The conclusion drawn is "NFRs are inherently difficult" rather than "the practice never had a scoring instrument that forced NFRs to be measurable enough to validate against."

The *architectural* alternative is to score NFRs against a structured per-attribute rubric. The scorecard enumerates a fixed set of quality attributes — drawn from a recognised vocabulary like ISO/IEC 25010 — with a published target per attribute expressed in measurable terms, not adjectives. Each attribute carries three states: specified (the target exists in the design artefact), validated in test (the target is exercised in a representative test environment with passing results), and operating in production (the target holds against real production load and traffic patterns). Scores are tracked across release cycles so the team can see whether availability is improving, latency is degrading, or scalability targets are being met as load grows. Trade-offs between attributes are articulated explicitly — increasing a latency target tightens the upper bound on cache strategies that would otherwise improve cost, and that trade-off appears in the scorecard rather than disappearing into an averaged-away "system quality" rating.

This is *not* a checklist. A checklist is a binary instrument: each item is met or not met, and the action is to flip the unchecked items. NFRs are not binary; latency is not "fast" or "slow" but a continuous distribution with percentiles and tail behaviour. The scorecard captures the continuous nature of NFRs: a P95 latency target of 250 ms, a current measurement of 320 ms, and a delta of 70 ms that informs prioritisation. A checklist would force this into a binary "latency target met / not met," losing the magnitude information that makes the scorecard actionable.

It is also *not* the same as a qualitative trade-off analysis like ATAM. ATAM is a structured workshop where stakeholders articulate quality attribute scenarios, identify architectural decisions that drive sensitivity to those scenarios, and surface trade-offs through guided discussion. The output is a qualitative document that informs architectural decisions. The NFR scorecard is the *quantitative* counterpart: once attributes are articulated through ATAM-style work, the scorecard tracks the measurable targets and validation states across the system's lifetime. ATAM produces the attributes and the targets; the scorecard validates them.

The architectural signature of a real NFR scorecard is that it answers, for any given release, the question "which NFRs are violated, by how much, and against what test or production evidence?" Without the scorecard, that question gets answered by tribal knowledge — the on-call engineer recalls the recent latency complaints, the SRE recalls the recent availability incidents, the security engineer recalls the recent control gaps. With the scorecard, the answer is structured, current, and acted upon as a release-blocker or release-conditional rather than as background noise.

## Six principles

### 1. NFRs are scored per attribute, never aggregated into a single quality rating
A "system quality score of 3.5" is meaningless because the engineering action implied by a low score in latency is completely different from the action implied by a low score in compliance. The scorecard preserves per-attribute scores throughout — performance, availability, scalability, security, observability, maintainability — and never collapses them. Roll-up reports show all attributes as separate columns, never as a single number.

#### Architectural implications
Each attribute has its own validation pathway: latency is validated by load tests at representative traffic patterns, availability is validated by chaos engineering and production incident history, security is validated by control assessment and threat modelling outcomes. The scorecard maintains these distinct pathways rather than collapsing them into a single QA stage.

#### Quick test
Ask the practice for the most recent NFR scorecard for a system. If it presents per-attribute scores with explicit deltas to targets, the discipline is in place. If it presents a single rolled-up rating, the per-attribute discipline has degraded.

#### Reference
[ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) defines a structured taxonomy of quality characteristics — the foundational vocabulary that NFR scorecards inherit and operationalise.

### 2. Each attribute has a measurable target alongside its qualitative level
A score of 4 out of 5 on availability is half-information; without the target, "4/5" cannot be acted upon. The scorecard pairs every qualitative score with the specific measurable target: availability target 99.95% with score 4 indicating current measured availability of 99.93%; latency P95 target 250 ms with score 3 indicating current P95 of 310 ms. Targets are expressed as percentile latencies, percent availability, throughput in requests per second, recovery time objectives in minutes, never as adjectives.

#### Architectural implications
Targets are themselves decisions with rationale. The scorecard records when a target was set, by whom, and against what business or user need. A target like "P95 latency 250 ms" came from a specific user-experience research finding, a competitive benchmark, or a contractual SLA — and that provenance is the artefact that justifies the target's continued relevance.

#### Quick test
For each attribute on the scorecard, ask the practice when the target was set and against what rationale. If targets have provenance and a last-reviewed-date, the discipline is in place. If targets are inherited from prior designs without rationale, they are folklore.

#### Reference
[Google SRE Workbook — SLOs](https://sre.google/workbook/implementing-slos/) describes the discipline of setting measurable service-level objectives derived from user-facing service-level indicators — the same standard NFR targets must meet.

### 3. Scoring distinguishes specified, validated in test, and operating in production
Three columns, three independent scores. Specified means the target exists as a published artefact and the team has agreed to it. Validated in test means a test exercise has demonstrated the target is achievable in a representative environment. Operating in production means observability data shows the target holds against real traffic and workload over a meaningful window. A target can be specified but not validated — the team agreed to a target the test environment cannot exercise. A target can be validated in test but not operating in production — the test traffic patterns differed from production traffic patterns. The scorecard surfaces these gaps rather than collapsing the three states into a single "achieved" indicator.

#### Architectural implications
Closing the gap between specified and validated is a test-environment investment. Closing the gap between validated and operating is a production-readiness investment, often involving observability instrumentation, chaos engineering, and SLI definition. The scorecard makes these investments visible as concrete deltas rather than as generic "improve quality" requests.

#### Quick test
Pick an availability target on the current scorecard. Ask: is this validated in test, and is it operating in production? If the answer is "we know the target but we don't have evidence on either," the three-column distinction has not been adopted.

#### Reference
[Quality Attribute Workshop (SEI)](https://insights.sei.cmu.edu/library/quality-attribute-workshop-third-edition-participants-handbook/) covers the practice of identifying quality attributes, articulating their scenarios, and tracking their resolution states through development — analogous to the specified/validated/operating progression.

### 4. The scorecard tracks NFRs across release cycles, not at a single point in time
A snapshot of NFRs at a single release tells you what is true now. A series of snapshots across releases tells you whether the system is improving or degrading on each attribute, and at what rate. The scorecard is a tracked artefact: each release produces a new column, prior columns persist, and trends become a primary signal. Latency degrading over four releases is more important than latency missing the target in any single release; it indicates an architectural issue that fixes-per-release are not addressing.

#### Architectural implications
The NFR scorecard becomes a release-trend artefact alongside test results and deployment metrics. Trends inform planning: an availability trend that worsens by 0.05% per release for four consecutive releases triggers an investment review even if the absolute level still meets the target. The scorecard is forward-looking, not just retrospective.

#### Quick test
Look at the NFR scorecard for the past six releases. If each attribute has a trend line, the per-release tracking is in place. If you see only the current release's snapshot, longitudinal discipline is missing.

#### Reference
[CISQ Software Quality Standards](https://www.it-cisq.org/standards/) define measurable quality factors that organisations track over time as part of governance, with explicit emphasis on trend tracking for early warning.

### 5. Trade-offs between attributes are made explicit, not hidden in averages
Some quality attributes naturally trade against each other. A tighter latency target may force in-memory caching that increases memory cost and degrades fault recovery. A higher availability target may require additional replicas that increase operational complexity and cost. The scorecard captures these trade-offs explicitly: when an attribute target is raised, the scorecard records which other attributes are affected and by how much. The trade-off becomes a documented architectural decision rather than an emergent surprise when the second-order attribute starts missing its target.

#### Architectural implications
Trade-off rows in the scorecard reference ADRs that justified the trade-off. When an attribute that was traded-against starts missing its target consistently, the scorecard surfaces the original trade-off decision and triggers revisitation.

#### Quick test
Ask the practice when the latency target last changed and what other attributes that change affected. If the answer references an ADR or trade-off discussion, trade-offs are explicit. If the answer is "I don't know — the target has been there for a while," trade-offs are implicit and likely violated.

#### Reference
[Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) describes the formal practice of identifying and analysing quality attribute trade-offs as a designed analytical activity rather than as accidental discovery.

### 6. The scorecard captures what the team learned from validation, not just what was achieved
Each release-cycle entry on the scorecard records, alongside the score, what the team learned during the validation. Sometimes the learning is "target was achievable with the planned design changes." Sometimes the learning is "target was achievable only after an unplanned cache layer was added — the original architecture would not have met the target without that addition." The captured learnings become the artefact that informs future target-setting and architectural decisions. Without them, each new release relearns the same lessons.

#### Architectural implications
Learnings become a teaching artefact for incoming engineers and for cross-system pattern dissemination. A learning about a cache layer required to meet latency targets in one system may apply to other systems with similar characteristics, and the scorecard's learning column makes the cross-system transfer possible.

#### Quick test
Look at last quarter's NFR scorecards across three systems. If learnings are captured as a separate column with substantive entries, the discipline is in place. If only scores appear with no learnings, validation is happening but its outputs are being thrown away.

#### Reference
[arc42 Architecture Template](https://arc42.org/) emphasises capturing architectural decisions and their rationale as durable artefacts — the same discipline applied to NFR validation outcomes.

## Common pitfalls when adopting NFR scorecards

### ⚠️ Treating NFRs as architectural assumptions rather than testable requirements
NFRs documented as adjectives in a design document are wishes. The discipline of expressing them as measurable targets and validating them in test environments is what converts them into requirements. The scorecard's measurable-targets discipline forces this conversion; without it, NFRs remain decorative.

### ⚠️ Specifying NFRs without targets — "must be fast"
"Fast" is not a target. "P95 latency under 250 ms at 1000 requests-per-second sustained load" is a target. The scorecard rejects untargeted attributes because they cannot be scored, validated, or trended. Untargeted attributes are an indication that the team has not yet done the user-research or business analysis required to specify the target.

### ⚠️ Aggregating NFR scores into a single number
A composite quality score of 3.5 has no engineering action attached to it. The scorecard's discipline is to never aggregate; per-attribute scores are the unit of action.

### ⚠️ Scoring at design time but never validating in production
A target specified in design with no production validation is an unverified assumption. The three-column discipline (specified / validated / operating) prevents the scorecard from registering green when only the first column is filled.

### ⚠️ NFR scorecard drift — old targets, new system
Targets persist across releases without revisitation. The system grows in scope, traffic patterns change, user expectations shift, and the targets that were appropriate two years ago no longer reflect business reality. The scorecard's last-reviewed-date discipline forces periodic target revisitation rather than letting the targets calcify.

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Fixed attribute set is published ‖ Six to ten quality attributes drawn from ISO/IEC 25010 (or equivalent vocabulary) are documented as the practice's NFR scorecard. The set is versioned, with deliberate change control. | ☐ |
| 2 | Each attribute has a measurable target with provenance ‖ Targets are expressed as percentile latencies, percent availability, throughput, RTOs in minutes — never as adjectives. Each target has a recorded provenance: business need, user research, contractual SLA, or competitive benchmark. | ☐ |
| 3 | Three-column tracking is in place: specified / validated / operating ‖ Each attribute has three independent scores. The columns are not collapsed; differences between them surface investment requirements. | ☐ |
| 4 | Validation pathways exist per attribute ‖ Latency has a load-testing pathway, availability has a chaos-engineering pathway, security has a control-assessment pathway. The scorecard is fed by these pathways, not by manual annotation. | ☐ |
| 5 | Production telemetry maps to operating-column scores ‖ SLIs in production observability roll up to the operating column. The scorecard's operating column is data-driven, not engineer-attestation. | ☐ |
| 6 | Per-release tracking with trend lines ‖ Each release produces a new scorecard entry. Prior entries persist. Trends per attribute are visualised over the trailing six-to-twelve releases. | ☐ |
| 7 | Trade-offs are documented in linked ADRs ‖ When a target is changed, the scorecard records which other attributes the change affects. The change is justified in an ADR; the scorecard links to it. | ☐ |
| 8 | Learnings are captured per release ‖ Validation outcomes generate learning entries on the scorecard, not just numerical updates. Learnings inform future target-setting and architectural decisions. | ☐ |
| 9 | Targets are revisited on a cadence ‖ At least annually, each target's provenance is reviewed against current business reality. Targets without current rationale are revised or sunset. | ☐ |
| 10 | The scorecard drives release-conditional gating ‖ A target missing in operating column for two consecutive releases triggers a release-conditional investigation. The scorecard is consequential to release decisions, not merely informational. | ☐ |

---

## Class Diagram

The class diagram below shows the structural schema of an NFR scorecard — the entities (Attribute, Target, ValidationState, Score, Trend) and their relationships. A class diagram fits because the scorecard is fundamentally a typed schema with structured relationships, not a workflow or hierarchy.

## Related

- [Scorecards: Architecture Review Scorecard](../architecture-review/) — the broader review-time scoring instrument that NFR scorecards feed into
- [Scorecards: Principles Scorecard](../principles/) — the parallel adherence-measurement instrument for architectural principles
- [Observability: SLI/SLO](../../observability/sli-slo/) — the production observability primitives that feed the operating-column scores
- [Templates: Review Template](../../templates/review-template/) — the document format that surfaces NFRs for review

## References

1. [ISO/IEC 25010 (Software Quality Model)](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) — *iso25000.com*
2. [CISQ Software Quality Standards](https://www.it-cisq.org/standards/) — *it-cisq.org*
3. [Quality Attribute Workshop (SEI)](https://insights.sei.cmu.edu/library/quality-attribute-workshop-third-edition-participants-handbook/) — *sei.cmu.edu*
4. [ATAM at SEI](https://insights.sei.cmu.edu/library/atam-criteria-evaluation-of-software-and-system-architectures/) — *sei.cmu.edu*
5. [Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) — *en.wikipedia.org*
6. [Google SRE Workbook — SLOs](https://sre.google/workbook/implementing-slos/) — *sre.google*
7. [Web Vitals (Google)](https://web.dev/articles/vitals) — *web.dev*
8. [arc42 Architecture Template](https://arc42.org/) — *arc42.org*
9. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
10. [DORA Capabilities Catalog](https://dora.dev/capabilities/) — *dora.dev*
