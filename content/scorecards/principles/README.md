# Principles Scorecard

The strategic guide for principles adherence scorecards — recognising that the team's per-principle scoring rather than aggregated adherence ratings, the graded levels across distinguishable adherence tiers rather than binary pass/fail, the per-release tracking that shows adherence trends rather than single snapshots, the evidence requirements that point to specific design choices rather than reviewer recollection, the explicit categorisation of deviations as deliberate trade-offs, oversights, or drift, and the architectural debt classification with concrete remediation deadlines are what determine whether architectural principles operate as living disciplinary instruments that shape multi-year design decisions or whether they degrade into wall-art slogans that nobody references because adherence was never honestly measured.

**Section:** `scorecards/` | **Subsection:** `principles/`
**Alignment:** Continuous Architecture in Practice | arc42 | CISQ Software Quality Standards | ISO/IEC 25010 | Architecture Decision Records (ADR community)
---

## What "principles scorecard" means — and how it differs from principle definitions and review scorecards

A *primitive* approach to architectural principles is to author them once — typically as a workshop output early in a platform's life — print them on a poster, reference them aspirationally in design decks, and assume that articulating the principles is sufficient to make them operative. Over months and years, individual designs cite the principles approvingly while quietly violating them, the principles continue to appear on the poster, and when an architect points out that the system has drifted away from "loose coupling" or "single source of truth," the response is "yes, those are aspirational." The principles become aspirational artefacts that live in slide decks but not in the system. After three years the team can no longer answer the question "do our systems adhere to our principles?" because nobody has ever measured. The conclusion drawn is "principles are inherently soft" rather than "the practice never had a scoring instrument that would have made principle adherence visible enough to manage."

The *architectural* alternative is to score adherence to each principle on a structured graded scale, separately, across releases. The scorecard enumerates each principle the practice has committed to and assigns a per-principle score reflecting how the current design of the system aligns with the principle. Scoring is graded — typically five levels — distinguishing the system that ignores the principle from the one that applies it inconsistently from the one that applies it with documented exceptions from the one that exemplifies it. Scores require evidence: which design choices indicate adherence, which indicate deviation. Deviations are categorised: deliberate trade-off (an ADR justifies the deviation against a higher-priority principle), oversight (the principle was not considered during design), or drift (the system was originally adherent and gradually moved away). Each category implies a different remediation path, and the scorecard tracks remediation as architectural debt with deadlines.

This is *not* the same as the principle definitions. Pages like `principles/foundational`, `principles/cloud-native`, and `principles/ai-native` are where the principles themselves are articulated — what each principle means, why it matters, when to apply it, when it conflicts with other principles. Those pages are the *content* that the scorecard measures against. A practice can have well-articulated principle definitions with no measurement (then the principles are decorative) and a practice can attempt to measure principles that are vaguely defined (then the measurement is unreliable). Both are required; this page covers the measurement instrument.

It is also *not* the same as the architecture review scorecard (`scorecards/architecture-review`). The review scorecard scores designs across multiple dimensions including functional fit, NFR coverage, operability, and others — principles adherence may be one dimension among them. The principles scorecard zooms into principles specifically, with one row per principle. The two scorecards interlock: the review scorecard's principles-adherence dimension is informed by the principles scorecard's per-principle history. A design that scores low on principles-adherence in a review prompts the principles scorecard to capture which principle(s) and at what severity.

It is also *not* a strategy artefact like `strategy/principles`. The strategy/principles page covers meta-principles for *how strategy itself works* — how strategic intent connects to structural decisions, how strategy cycles run. The principles scorecard measures *adherence of designs to architectural principles* — operational measurement at design altitude, not meta-strategic discipline.

The architectural signature of a real principles scorecard is that it answers, for any principle the practice has committed to, the question "across the systems we operate, what is the distribution of adherence and what is the trend?" Without the scorecard, every principle becomes equally aspirational regardless of how widely violated; with the scorecard, the practice can target investment at the principle most weakly adhered to and watch adherence improve.

## Six principles

### 1. Each principle gets its own scoring dimension; principles are not aggregated
A "principles adherence rating of 3.5" mixes a strong score on observability with a weak score on loose coupling. The engineering action implied by improving observability is unrelated to the action implied by improving coupling, and aggregating the two destroys the actionability. The scorecard maintains per-principle scores throughout — one row per principle, one score per release, no averaging into composites.

#### Architectural implications
Each principle has its own remediation pathway. Improving observability adherence requires telemetry instrumentation work; improving coupling adherence may require module refactoring, interface design discipline, or service decomposition. The scorecard preserves these distinct pathways rather than collapsing them into "improve architectural quality."

#### Quick test
Look at the most recent principles scorecard. If each principle has an explicit per-principle score with a delta to the prior release, the per-principle discipline is in place. If only an aggregate adherence rating is reported, the discipline has been lost.

#### Reference
[Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) emphasises that architectural principles are operative only when adherence is observable per principle — the foundation of per-principle scoring discipline.

### 2. Adherence is graded across distinguishable levels, not binary pass/fail
"Does the system adhere to the principle of single source of truth?" admits no useful binary answer. Almost every system adheres in some respects and deviates in others. A binary scorecard forces the assessment into a pass label that hides the deviations or a fail label that hides the genuine adherence. The graded scale — typically five levels — gives the scorecard the resolution to capture the system's actual state. Common rubric: 1 means the principle is systematically violated; 2 means the principle is acknowledged but not applied; 3 means the principle is applied in some areas, violated in others, with no documentation of which is which; 4 means the principle is applied consistently except for documented trade-offs; 5 means the principle is applied with explicit exception handling and the exceptions themselves are reviewed periodically.

#### Architectural implications
The graded scale becomes the calibration target — the practice learns what each level means by scoring many systems against it. Reviewers come to share an understanding of the difference between a 3 and a 4 that a binary scale would never have surfaced.

#### Quick test
Pick a principle on the current scorecard with score 3. Ask: what would it take to move the score to 4? If the answer is specific and tied to documentation or exception-handling discipline, the graded scale is operational. If the answer is general improvement language, the levels are not distinct in practice.

#### Reference
[Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) provides the lineage for graded maturity scales applied to processes — analogous discipline applied to principle adherence.

### 3. The scorecard tracks adherence trends across releases, not single snapshots
A snapshot of adherence at a single release describes the current state. A series of snapshots across releases describes the trajectory: is adherence improving on each principle, holding steady, or degrading? Trends are the primary signal for many decisions. Adherence to single-source-of-truth degrading over four releases — even if the absolute level is still 3 — suggests something architectural is undermining the principle and warrants investigation before the score reaches 2.

#### Architectural implications
The scorecard becomes a release-trend artefact. Trends inform planning: a principle whose adherence has fallen for three consecutive releases triggers an investment review and a potential ADR documenting why the principle is being relaxed (if the trend is intentional) or what remediation is being scheduled (if it is not).

#### Quick test
Look at the principles scorecard for the past six releases. If each principle has a trend line, longitudinal tracking is in place. If only the current release's snapshot is visible, the practice is single-pointing.

#### Reference
[CISQ Software Quality Standards](https://www.it-cisq.org/standards/) emphasise trend tracking of measurable quality factors over time as a core governance discipline — directly applicable to principle adherence trends.

### 4. Scoring requires evidence — which design choices indicate adherence or deviation
A score of 3 on loose coupling that cannot be justified by pointing to specific module boundaries, dependency directions, or interface contracts is a vote, not an assessment. The scorecard discipline is to require, alongside each score, a citation of the evidence: the architecture diagram showing the boundary, the dependency-analysis output showing the direction, the API contract showing the interface. When the evidence is thin, the score notes that fact — the score becomes a low-confidence rating that may resolve up or down when evidence is gathered.

#### Architectural implications
Evidence requirements feed back into architecture documentation discipline. A practice that cannot evidence its scores must invest in dependency analysis tooling, architecture diagramming standards, and interface documentation — the scorecard makes the gaps visible as concrete deltas.

#### Quick test
For a recent principle score, ask the assessor what evidence supported the score. If they can point to specific design artefacts, the discipline is in place. If they offer general impressions, the discipline is not applied.

#### Reference
[arc42 Architecture Template](https://arc42.org/) provides documentation conventions that surface the evidence required for principle-adherence scoring — diagrams, ADRs, interface specifications.

### 5. Principle deviations are categorised: deliberate trade-off, oversight, or drift
A deviation from a principle is not a single thing. A deliberate trade-off is a deviation that was considered, articulated, and chosen against a higher-priority concern — typically captured in an ADR. An oversight is a deviation that was not considered during design — the principle simply did not enter the conversation. A drift is a deviation that emerged over time as the system evolved — the principle was originally adhered to and the adherence eroded incrementally. Each category implies a different remediation: trade-offs are revisited periodically as the trade-off conditions change; oversights are corrected in the next revision; drifts are addressed through architectural intervention or re-articulation of the principle.

#### Architectural implications
The category becomes the basis for prioritisation. Drifts are typically the highest-priority remediation because they are unintentional and indicate the system is becoming less coherent over time. Trade-offs are the lowest-priority because they were already considered. Oversights fall in between — fixable with focused work, but not urgent unless the deviation is causing material harm.

#### Quick test
Look at the deviations recorded for a recent system. If each is categorised and the category drives a specific remediation type, the discipline is in place. If deviations are recorded uniformly without categorisation, the practice misses the prioritisation signal.

#### Reference
[Architecture Decision Records (ADR community)](https://adr.github.io/) provides the artefact discipline for capturing deliberate trade-offs — the canonical evidence for the trade-off category.

### 6. The scorecard drives architectural debt classification with concrete remediation deadlines
Each below-threshold score generates an architectural debt item. The debt has a description (which principle, what level, what evidence), a remediation pathway (what work would move the score up), an owner, and a target deadline. Debt is tracked separately from the principle scores themselves so that the scorecard can show both the current state and the planned remediation trajectory. Deadlines are real — debt that consistently misses its deadline triggers escalation to the practice leadership rather than quiet roll-over.

#### Architectural implications
Architectural debt becomes a managed portfolio. The aggregate debt across the practice is visible and trended; debt growth indicates the practice is accumulating violations faster than remediating them. The debt portfolio is reviewed at the practice level on a cadence and informs platform investment decisions.

#### Quick test
Look at the architectural debt register for one system. If each item is tied to a principle deviation, has a deadline, and a tracked status, the discipline is in place. If debt is recorded vaguely with no deadlines, the scorecard's debt-driving function is decorative.

#### Reference
[Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) covers architectural debt as a managed concept distinct from technical debt at the code level — analogous to the principle-adherence debt the scorecard surfaces.

## Common pitfalls when adopting principles scorecards

### ⚠️ Principles that cannot be objectively scored
A principle phrased as "we believe in pragmatism" or "we value simplicity" cannot be scored because no observable indicators exist. The scorecard discipline forces principle definitions to be operationalisable — phrased as testable or observable assertions. Principles that cannot be operationalised are aspirational statements, not architectural principles.

### ⚠️ Principle adherence as a passing grade (binary)
Treating adherence as binary loses the gradient that makes the scorecard actionable. A binary "the system adheres" hides the deviations that matter; a binary "the system fails to adhere" hides the genuine adherence. The graded scale is the discipline that makes adherence visible at the resolution required for prioritisation.

### ⚠️ Aggregating principle scores into a single design quality score
A composite "principle adherence rating of 3.5" obscures whether the system is uniformly mediocre or strong on some principles and weak on others. Per-principle scores remain the unit of action; aggregates are at most a roll-up reporting view, never a basis for engineering decisions.

### ⚠️ Scoring without distinguishing exception, trade-off, and drift
A deviation logged as "system does not adhere to single-source-of-truth" without category does not tell the practice whether to revisit the trade-off, fix the oversight, or address the drift. The category is the prioritisation signal; without it, all deviations look equally remediable, which makes none of them actually remediable.

### ⚠️ Principle scorecards that don't track over time
A scorecard refreshed for each release without preserving prior releases loses the trend signal. A principle whose adherence is degrading slowly may show acceptable scores in any single release but reveal a pattern across releases. Without the longitudinal record, the pattern is invisible until it manifests as architectural failure.

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Principles are operationalisable ‖ Each principle on the scorecard is phrased as a testable or observable assertion. Principles that cannot be operationalised are flagged and either re-articulated or removed from the scorecard. | ☐ |
| 2 | Per-principle scoring with graded levels ‖ Each principle has its own row with a five-level (or equivalent) graded scale. Binary pass/fail is not used. The level definitions are published with concrete observable indicators. | ☐ |
| 3 | Evidence is required for each score ‖ Score annotations cite specific design artefacts: diagrams, ADRs, dependency analyses, interface contracts. Scores without evidence are flagged as low-confidence. | ☐ |
| 4 | Deviations are categorised: trade-off / oversight / drift ‖ Each below-threshold score includes a deviation category. The category drives the remediation type. Uncategorised deviations are the exception, not the norm. | ☐ |
| 5 | Per-release tracking with trend lines ‖ Each release produces a new scorecard entry per principle. Prior entries persist. Trends are visualised over the trailing six-to-twelve releases. | ☐ |
| 6 | Architectural debt items per below-threshold principle ‖ Each below-threshold score generates a debt item with description, remediation pathway, owner, and deadline. Debt is tracked separately from scores. | ☐ |
| 7 | Trade-off deviations link to ADRs ‖ A deviation categorised as trade-off references the ADR that justified it. Trade-offs without ADRs are reclassified as oversights or drifts. | ☐ |
| 8 | Drift deviations trigger architectural review ‖ A principle whose adherence has degraded across multiple releases without explicit re-articulation triggers a focused architectural review at the practice level. | ☐ |
| 9 | The scorecard is published per system on a cadence ‖ Each system in the practice has a current principles scorecard updated at a published cadence — typically per release or quarterly. The cadence is honoured rather than skipped. | ☐ |
| 10 | Aggregate debt is reviewed at practice level ‖ The total architectural debt across systems is reviewed periodically by practice leadership. Debt growth informs platform investment decisions and capability development. | ☐ |

---

## Flowchart

The flowchart below shows the principles-scorecard assessment workflow — from identifying which principles apply, through scoring each one with evidence, classifying any deviations, generating debt items, and tracking remediation. A flowchart fits because the scorecard's value is fundamentally a *workflow*: the scoring is one step in a longer chain that connects principle definitions to architectural debt classification and remediation tracking.

## Related

- [Scorecards: Architecture Review Scorecard](../architecture-review/) — the broader review-time scoring instrument; principles adherence is one dimension among several
- [Scorecards: NFR Scorecard](../nfr/) — the parallel measurement instrument for non-functional requirements
- [Principles: Foundational](../../principles/foundational/) — the principle definitions that this scorecard measures adherence to
- [Strategy: Strategy Principles](../../strategy/principles/) — the meta-principles for how strategy work runs, distinct from architectural principles measured here

## References

1. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
2. [arc42 Architecture Template](https://arc42.org/) — *arc42.org*
3. [CISQ Software Quality Standards](https://www.it-cisq.org/standards/) — *it-cisq.org*
4. [ISO/IEC 25010 (Software Quality Model)](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) — *iso25000.com*
5. [Architecture Decision Records (ADR community)](https://adr.github.io/) — *adr.github.io*
6. [Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) — *en.wikipedia.org*
7. [TOGAF (overview)](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) — *en.wikipedia.org*
8. [Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) — *en.wikipedia.org*
9. [ATAM at SEI](https://insights.sei.cmu.edu/library/atam-criteria-evaluation-of-software-and-system-architectures/) — *sei.cmu.edu*
10. [DORA Capabilities Catalog](https://dora.dev/capabilities/) — *dora.dev*
