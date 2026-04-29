# Architecture Review Scorecard

The strategic guide for architecture review scorecards — recognising that the team's small fixed set of dimensions chosen to cover the design space without overlap, the explicit unambiguous scoring criteria that every reviewer applies the same way, the evidence anchoring that points to the design artefact rather than reviewer intuition, the uncertainty annotations alongside scores that distinguish confident from speculative ratings, the comparison to organisation baselines rather than abstract external standards, and the dimension-level action items that drive concrete follow-through rather than aggregate verdicts are what determine whether architecture reviews produce institutional learning that improves designs over time or whether they degrade into ceremonial passing grades that nobody acts on because the scoring instrument never disciplined the conversation.

**Section:** `scorecards/` | **Subsection:** `architecture-review/`
**Alignment:** ISO/IEC 25010 | ATAM (SEI) | arc42 | Continuous Architecture in Practice | DORA Capabilities Catalog
---

## What "architecture review scorecard" means — and how it differs from review templates and governance scorecards

A *primitive* approach to architecture review is to convene the senior architects, walk through the design slide-by-slide, ask probing questions, and emit a verbal verdict — "this looks fine to proceed" or "we have concerns." The verdict is delivered, the team makes some adjustments, and the design moves into implementation. After the system ships and an outage or audit reveals an issue that should have been caught at review, the team performs a post-mortem and concludes "the review missed this dimension." A new dimension is added to the next review's checklist. After eighteen months of accumulating concerns, every review covers thirty open-ended dimensions, takes four hours, produces no consistent outcome, and is felt by both reviewers and reviewees as bureaucratic friction with no proportional benefit. The conclusion drawn is "architecture reviews don't scale" rather than "the review process never had a calibrated scoring instrument that would have made the conversation reproducible across reviewers and across designs."

The *architectural* alternative is to design the architecture review as a structured assessment driven by an explicit scorecard. The scorecard is a small fixed set of dimensions — typically five to seven — chosen to span the design space without overlap. Each dimension has a published rubric specifying what each score means, with concrete observable indicators per level. Reviewers score each dimension against the design artefact (the proposal document, the C4 diagrams, the NFR specification) rather than against their personal sense of "good architecture." Scores include uncertainty annotations distinguishing high-confidence ratings (the evidence is in the artefact) from low-confidence ones (the artefact is silent and the score reflects what reviewers believe is implied). Aggregate verdicts — pass / pass-with-conditions / revise / reject — derive from explicit aggregation rules over dimension scores, not from a holistic gut check. Each dimension that scores below threshold produces a specific action item that is tracked to closure, separate from the verdict itself.

This is *not* the same as the review template (`templates/review-template`). The template is the document format in which a design proposal is presented for review — sections for context, decision drivers, constraints, options, the chosen design, NFR coverage, and so on. The template is the *input* to the review. The scorecard is the *instrument* the reviewers use to assess what the template contains. A team can have a beautifully structured review template that no scorecard is applied to (then the template is preparatory ceremony) and a team can have a calibrated scorecard with no template (then reviewers score whatever shows up). Both pieces are required; this page covers the scorecard, and the template is a separate craft.

It is also *not* the same as a governance scorecard (`governance/scorecards`). A governance scorecard measures whether the architecture *governance system itself* is working — are reviews happening at the right cadence, are decisions being recorded, is the practice covering the right scope of work. The architecture review scorecard measures *individual designs* coming through the system. The two scorecards are at different altitudes and serve different audiences: governance scorecards drive practice-level investment, review scorecards drive design-level decisions.

The architectural signature of a real review scorecard is *reproducibility*. Two different reviewers scoring the same design against the same scorecard produce comparable scores, with disagreements concentrated in specific dimensions where the rubric is being clarified. The same reviewer scoring two different designs produces comparable scores when the designs have comparable architectural quality. Without that reproducibility, every review is a performance — interesting, possibly useful, but not an instrument that can produce trend lines, calibrate teams, or accumulate organisational learning.

## Six principles

### 1. Dimensions are a fixed small set, chosen to cover the design space without overlap
A scorecard with thirty open-ended dimensions is not a scorecard; it is a wishlist. The first design choice for a useful review scorecard is to commit to a small fixed set — typically five to seven dimensions — that together cover the architecturally significant aspects of any design the practice reviews. The dimensions are chosen to be *orthogonal*: scoring high on one does not mechanically improve the score on another. Common dimension sets include something like: functional fit, architectural fit (alignment to platform and patterns), NFR coverage, operability, security and compliance, and cost or sustainability. The exact set is a deliberate choice for the practice and a published artefact, not something each reviewer assembles in the moment.

#### Architectural implications
The fixed dimension set becomes a calibration target — reviewers learn what each dimension means by scoring many designs against it. Adding a new dimension is a high-cost decision that requires retraining all reviewers on the new rubric and risks invalidating prior trend lines. Dimensions are removed when post-hoc analysis shows they consistently track perfectly with another dimension (the orthogonality assumption was wrong) or consistently produce no decision-affecting variation across designs (the dimension is not architecturally significant for what this practice reviews).

#### Quick test
Show three reviewers a recent design and ask them to list the dimensions they would score. If the three lists are different by more than one or two dimensions, the practice does not have a fixed dimension set.

#### Reference
[arc42 Architecture Template](https://arc42.org/) organises architecture documentation around a fixed set of sections that map naturally to review dimensions. [ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) provides a vocabulary for quality characteristics that informs dimension selection without prescribing a specific scorecard.

### 2. Each dimension has explicit, unambiguous scoring criteria visible to all reviewers
A dimension labelled "Operability" with no rubric is not a scoring dimension; it is a topic for unstructured discussion. The scorecard's design discipline is to publish, alongside each dimension, what each score means in observable terms. A typical five-level scale: 1 means architectural-debt is being created and the design will need rework before it ships; 2 means significant gaps that must be addressed but not blocking; 3 means meets minimum bar with explicit conditions; 4 means meets expectations with no significant gaps; 5 means exemplary, would be cited as a reference design for future work. Each level for each dimension has two or three concrete observable indicators ("design includes runbook for top three failure modes" rather than "system is operable").

#### Architectural implications
The rubric is a versioned artefact. Changes to it are explicit decisions, with rationale and a calibration cycle to recalibrate reviewers. The rubric becomes the durable artefact of how the practice defines architectural quality — more durable than any individual review's findings.

#### Quick test
Pick a recent design that scored 3 on Operability. Ask the reviewer to point to the rubric criterion that justified that score. If the answer is general ("operability felt OK") rather than specific ("met indicators a and b, did not meet indicator c"), the rubric is not operational.

#### Reference
[Quality Attribute Workshop (SEI)](https://insights.sei.cmu.edu/library/quality-attribute-workshop-third-edition-participants-handbook/) describes the use of scenarios as concrete observable indicators for quality attributes — the same discipline applied to scorecard rubrics.

### 3. Scores are anchored to evidence in the design artefact, not reviewer intuition
A score that cannot be defended by pointing to the design artefact is a vote, not a measurement. The discipline is to require, for each dimension, that the reviewer cite the section of the design document, the C4 diagram, the NFR specification, or the ADR that supports the score. When the artefact is silent on a dimension, that fact is itself recorded — the score becomes "score with low confidence: artefact does not address this dimension." This is different from a low score; it is a low-confidence score that may resolve high or low when the gap is filled.

#### Architectural implications
The artefact requirements feed back into the review template. A template that does not surface the information needed to score the dimensions makes the scorecard impossible to apply, which forces template improvement. Reviewers should not be asked to infer NFR coverage from the diagrams; the template should require explicit NFR sections that the scorecard maps to.

#### Quick test
Read the comments on a recent review's scorecard. If most scores are accompanied by a section reference, paragraph quote, or diagram pointer, evidence anchoring is in place. If most scores are accompanied by general impressions or no annotation, the discipline is not applied.

#### Reference
[Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) emphasises that architectural decisions and their rationale are *recorded artefacts*, not tribal knowledge — the same standard that scorecard scores must meet.

### 4. Scores carry uncertainty annotations distinguishing confident from speculative ratings
Scoring without uncertainty annotations conflates two quite different findings: "this design has weak operability" versus "we cannot tell from the artefact whether this design has good or weak operability." Both look like a score of 2; the action items they imply are different. The first triggers design improvement work; the second triggers documentation improvement work. The scorecard captures uncertainty as a per-score confidence level (high / medium / low) so the action items are specific to the underlying finding.

#### Architectural implications
A pattern of low-confidence scores in a dimension across many reviews indicates that the review template is missing a section, not that the designs are weak. The aggregated uncertainty data drives template evolution rather than design rejection.

#### Quick test
Look at the review records for the past quarter. If you can categorise the action items into "improve the design" versus "improve the documentation," the scorecard captures uncertainty. If all action items conflate the two, it does not.

#### Reference
[Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) covers the formal practice of distinguishing risks (issues identified) from non-risks and sensitivity points — a vocabulary that maps directly onto confidence-annotated scoring.

### 5. Reviews compare designs to organisation baselines, not to abstract external standards
A score of 3 against a published rubric is more useful when the practice knows that 80% of recent designs scored 3 on this dimension and 4 on others, and that the baseline for designs of this category is 3.5. The scorecard becomes interpretable through the accumulated history of scores in the same organisation. Comparing a score against an external "industry standard" is much less useful — most external rubrics either describe an idealised state that few real systems achieve, or they bias toward specific technology stacks that may not apply.

#### Architectural implications
The practice maintains baseline distributions per dimension and per design category. New reviews are scored against the rubric, then plotted against baselines to inform the verdict. Trends in baselines over time become a separate signal: if the baseline for Operability is rising across recent designs, the practice is improving. If it is falling, something in the engineering environment changed and warrants investigation.

#### Quick test
Ask the practice lead what the baseline score is for Operability across recent designs. If a number is offered with rough confidence, baselines exist. If the answer is "we don't track that," scores are floating against an imagined ideal rather than calibrated to organisational reality.

#### Reference
[ATAM at SEI](https://insights.sei.cmu.edu/library/atam-criteria-evaluation-of-software-and-system-architectures/) describes evaluation against scenarios calibrated to specific stakeholder concerns — the same logic applied to organisation-specific baselines.

### 6. Dimension-level action items drive follow-through, not aggregate verdicts
A review that produces only an aggregate verdict — pass, pass-with-conditions, fail — provides no machinery for actually improving the design. The discipline is that each dimension scoring below the practice's threshold produces a specific action item with an owner, a deliverable description, and a closure criterion. The action items are tracked separately from the verdict; a design can be approved with conditions where the action items must close before some downstream gate, or a design can be rejected with action items that must be addressed before the next review. The aggregate verdict is a roll-up of the action items, not a holistic gut judgement.

#### Architectural implications
Action items become an organisational artefact: closure rates per dimension reveal where the practice has remediation muscle and where it does not. A dimension with consistently open action items is a teaching opportunity for the practice — the team understands what good looks like but cannot reliably get there.

#### Quick test
For a recent review, look at the action items. If each has an owner, a description specific enough to know when it is done, and a closure criterion, the discipline is in place. If action items are generic ("strengthen operability") with no owner or closure criterion, the review produced rhetoric, not a tracked output.

#### Reference
[Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) provides a framework for capability assessment with explicit improvement actions tied to identified gaps — analogous to dimension-level action items derived from review scoring.

## Common pitfalls when adopting architecture review scorecards

### ⚠️ Open-ended dimension sets that bloat over time
Each post-mortem identifies a dimension the review missed. The practice adds it to the scorecard. After eighteen months, the scorecard has thirty dimensions, the review takes four hours, no reviewer scores all of them carefully, and consistency collapses. The discipline is that adding a new dimension is a deliberate decision with a calibration cycle; an issue identified in post-mortem more often indicates a missing rubric criterion within an existing dimension rather than a missing dimension.

### ⚠️ Scoring without referencing the design artefact
Reviews where reviewers score from memory or general impression produce floating numbers that drift across reviewers. The discipline of citing the artefact for each score is what makes the scorecard reproducible across reviewers and across designs.

### ⚠️ Compressing multidimensional review into a single number
Aggregating six dimension scores into a single design quality number — "this design scored 3.8" — destroys the information the scorecard exists to surface. A 4 on functional fit and a 1 on operability average to 2.5; that average is meaningless. The verdict comes from explicit rules over the per-dimension scores, not from arithmetic on them.

### ⚠️ Reviews that produce verdicts but no follow-through
A practice where reviews approve designs with conditions, the conditions are noted in a wiki page, and nobody tracks closure has effectively no review. The conditions become decorative artefacts. Closure tracking is the discipline that converts review findings into design improvement.

### ⚠️ Calibration drift where reviewers anchor differently over time
Without calibration cycles, two reviewers scoring the same dimension drift apart over months as each builds individual interpretations of the rubric. The same reviewer scoring designs in October versus April applies subtly different standards. The remedy is periodic calibration sessions — typically quarterly — where the same recent designs are scored by all reviewers and disagreements drive rubric clarifications.

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Fixed dimension set is published ‖ Five to seven orthogonal dimensions are documented as the practice's review scorecard. The set is versioned, with deliberate change control. Adding a dimension requires rationale and a calibration cycle. | ☐ |
| 2 | Each dimension has a level-by-level rubric ‖ Five-level scale (or equivalent) per dimension, with two-to-three concrete observable indicators per level. The rubric is a published artefact reviewers learn against. | ☐ |
| 3 | Reviews require artefact-citation for each score ‖ Score annotations include section references, paragraph quotes, or diagram pointers. Scores without artefact references are not accepted into the review record. | ☐ |
| 4 | Confidence levels are recorded alongside scores ‖ Each score is high / medium / low confidence. Low-confidence scores trigger documentation action items rather than design action items. | ☐ |
| 5 | Baseline distributions are maintained per dimension ‖ The practice tracks rolling baselines (e.g., trailing twelve months) per dimension and per design category. New reviews are scored against the rubric then interpreted against baselines. | ☐ |
| 6 | Verdicts derive from explicit aggregation rules ‖ Pass / pass-with-conditions / revise / reject is determined by a published rule over dimension scores (e.g., no dimension below 2; at most one dimension below 3 with conditions). The verdict is not a separate gut judgement. | ☐ |
| 7 | Each below-threshold dimension produces an action item ‖ Action items have an owner, a closure criterion, and a tracked status. They are separate from the verdict and persist until closed. | ☐ |
| 8 | Action item closure is tracked organisationally ‖ Closure rates per dimension are a reported metric. Dimensions with consistently open action items become teaching opportunities for the practice. | ☐ |
| 9 | Calibration sessions run on a cadence ‖ At least quarterly, all reviewers score the same designs and discuss disagreements. Outputs are rubric clarifications and reviewer learnings, not just inter-rater reliability statistics. | ☐ |
| 10 | The scorecard versions itself with rationale ‖ Each rubric version has a changelog. Trend lines noting that "scores from version 2.x and version 3.x are not directly comparable" are honoured in baseline tracking. | ☐ |

---

## Mind Map

The mindmap below shows the structural decomposition of an architecture review scorecard — the dimensions and their sub-criteria. The shape is a tree because a scorecard is fundamentally hierarchical: the scorecard contains dimensions, each dimension contains criteria, each criterion has indicators.

## Related

- [Templates: Review Template](../../templates/review-template/) — the document format that a review scorecard is applied to
- [Governance: Scorecards](../../governance/scorecards/) — scorecards measuring whether the governance system itself is working, at a different altitude
- [Templates: ADR Template](../../templates/adr-template/) — the artefact that captures the decisions a review approves
- [Strategy: Strategy Principles](../../strategy/principles/) — the meta-principles for how strategic decisions including review-system design get made

## References

1. [ISO/IEC 25010 (Software Quality Model)](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010) — *iso25000.com*
2. [arc42 Architecture Template](https://arc42.org/) — *arc42.org*
3. [Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) — *en.wikipedia.org*
4. [ATAM at SEI](https://insights.sei.cmu.edu/library/atam-criteria-evaluation-of-software-and-system-architectures/) — *sei.cmu.edu*
5. [Quality Attribute Workshop (SEI)](https://insights.sei.cmu.edu/library/quality-attribute-workshop-third-edition-participants-handbook/) — *sei.cmu.edu*
6. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
7. [C4 Model](https://c4model.com/) — *c4model.com*
8. [Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) — *en.wikipedia.org*
9. [TOGAF (overview)](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) — *en.wikipedia.org*
10. [DORA Capabilities Catalog](https://dora.dev/capabilities/) — *dora.dev*
