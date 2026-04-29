# Maturity Guidelines

The strategic guide for using maturity models well — recognising that the team's deliberate selection of one model rather than a composite of many, the honest current-state assessment grounded in evidence rather than aspiration, the explicit target-state choice with rationale rather than a default of "everyone should reach level 5," the trajectory-over-snapshot interpretation that values rate-of-improvement above absolute score, the per-team calibration that prevents inter-team comparison from becoming theatre, and the assessment cadence that lets each cycle inform the next rather than producing identical numbers year after year are what determine whether maturity assessments drive real capability development that the organisation can feel in its delivery outcomes or whether they degrade into compliance rituals that produce ascending numbers on slides while the underlying engineering practice stagnates.

**Section:** `maturity/` | **Subsection:** `guidelines/`
**Alignment:** SEI CMMI | OWASP SAMM | DORA Capabilities | CNCF Cloud Native Maturity | AWS Well-Architected
---

## What "maturity guidelines" means — and how it differs from the maturity-models catalogue

A *primitive* approach to maturity assessment is to download a vendor's maturity model — usually a five-level rubric covering ten or so capability areas — distribute it as a self-assessment questionnaire, average the responses, and publish a number. Six months later, leadership asks why the next assessment didn't show improvement, the team scores themselves higher to satisfy the request, and the maturity number ascends. After eighteen months, the score is reliably climbing while delivery outcomes — lead time, change failure rate, mean-time-to-restore, security incidents — remain unchanged. The conclusion drawn is "maturity assessments don't predict outcomes" rather than "we ran an unwise assessment process around a model that probably wasn't even the right one for our context."

The *architectural* alternative is to treat maturity assessment as a deliberately designed *practice* with explicit guidelines about which model to pick, how to gather evidence, how to score honestly, how to interpret the result, and how to use the result to drive capability development. The model is the *instrument*; the guidelines are the *protocol* for using the instrument. A poorly chosen instrument used with a strict protocol still produces useful information; a well-designed instrument used carelessly produces noise dressed as signal.

This is *not* the same as the maturity-models catalogue ([`maturity/models`](../models)). That page documents the specific models available — CMMI, OWASP SAMM, DORA capabilities, CNCF Cloud Native, AI maturity frameworks — and helps you choose between them. This page documents *how to run a maturity assessment well, regardless of which model you have chosen*. The two pages are complementary: models is "what tools exist"; guidelines is "how to use any tool well."

This is also *not* the same as architecture review ([`scorecards/architecture-review`](../../scorecards/architecture-review)). Architecture review scores *individual designs*; maturity assessment scores *organisational capability across many systems and many teams over time*. The altitudes are different: review operates at design-decision granularity; maturity operates at programme-of-work granularity. A team can have rigorous reviews of every design and still have a low maturity score (because the review *practice* itself isn't institutionalised). A team can have a high maturity score and still ship bad designs (because the maturity rubric covered process and not design quality).

The architectural signature of well-run maturity assessment is *trajectory readability*. Two consecutive assessments produce comparable scores because the evidence base is comparable, the calibration is the same, and the assessors used the rubric the same way. Score *changes* between assessments are interpretable as real capability changes, not as scoring noise. Without that property, the assessment is producing data that looks like a trend but is actually a random walk.

## Six principles

### 1. Pick one model deliberately rather than composing a private one
The strongest temptation in a maturity programme is to take the best parts of three or four models and assemble a custom rubric. This is almost always a mistake. Public maturity models — CMMI, SAMM, DORA, CNCF Cloud Native — represent thousands of person-hours of calibration across hundreds of organisations. Their level-definitions, capability-area-decompositions, and evidence-types have been refined over decades. A private composite throws away that calibration in exchange for a rubric that "feels right to us," which usually means it scores us at a level we are comfortable with.

The deliberate choice is to pick one published model whose scope and altitude matches the question being asked, commit to using it as published, and accept that some areas will be poorly covered. Coverage gaps in the model are honest information about what the assessment can and cannot measure. They are preferable to private rubrics that pretend to measure everything and actually measure nothing reproducibly.

#### Architectural implications
Choosing a model is a multi-year commitment because trajectory readability depends on assessment-to-assessment comparability. Switching models invalidates the trend line. The model choice should therefore be made by the senior architecture practice, after explicit comparison of scope and altitude, and reviewed only when the underlying business-of-the-organisation changes substantially.

#### Quick test
Ask the architecture practice "which maturity model are we using?" If the answer is "we have our own framework based on several industry models," the practice has accidentally landed on a private composite. If the answer is "we use SAMM for security and CMMI for delivery process and DORA for DevOps and we composite the scores," that is also a private composite — three rubrics with incompatible level definitions and no validated aggregation rule.

### 2. Score against evidence in the artefact, not against reviewer recollection
A maturity rubric specifies what each level means and what evidence demonstrates that level. A rigorous assessment scores each capability area by examining the evidence — the runbook that exists or doesn't, the test pipeline that runs or doesn't, the post-incident review records that are filed or aren't, the ADR catalogue that is current or stale. A loose assessment scores by asking team members "do you feel this practice is mature?" and averaging the responses.

The first approach produces information about the system. The second produces information about how the team feels about the system, which correlates with maturity inconsistently and tracks team-confidence cycles more than capability cycles. New team members feel less mature; experienced team members feel more mature; neither is necessarily correct.

#### Architectural implications
The assessment process should require the assessor to cite specific evidence for each scored level — a runbook URL, a CI configuration file, a quarterly review meeting record. Scores without evidence are flagged as low-confidence and not aggregated into the trajectory line. This discipline is initially slow and produces lower scores than felt-maturity assessments. That is a feature, not a defect: the gap between felt maturity and evidenced maturity is itself architecturally significant information about how the team perceives its own capability versus what is actually institutionalised.

#### Quick test
Pick a recent maturity assessment result and look at the highest-scoring capability area. Ask the assessor what specific artefact was cited as evidence for that level. If the answer is a specific URL or document reference, the assessment is evidence-grounded. If the answer is "we rated ourselves high because the team has been doing this for a while," it is felt-maturity.

### 3. Choose the target state explicitly, with rationale, rather than defaulting to "everyone reaches level 5"
Every published maturity model has a top level. The temptation is to treat the top level as the goal for every capability area. This is almost always wrong. The top level represents capability that is appropriate for organisations whose business depends critically on that area. Most organisations have heterogeneous capability requirements: their core domain demands top-level capability; their supporting domains demand mid-level capability; their commodity domains demand baseline capability.

A well-run programme makes the target-state choice explicit per capability area, with rationale tied to the business-of-the-organisation. "Security incident response: target level 5 because we hold regulated data; supply-chain SBOM: target level 3 because we have low third-party-component diversity; release automation: target level 4 because release frequency is a competitive differentiator." The targets become the navigational chart; the assessment measures distance from each target rather than absolute level.

#### Architectural implications
The target-state document is itself an architectural artefact. It is reviewed by senior architecture, signed off by senior leadership, and updated when the business-of-the-organisation changes. Without a target-state document, every gap to level 5 looks equally important and the practice ends up investing equally in commodity-domain maturity and critical-domain maturity, which is the wrong allocation.

#### Quick test
Ask "what is our target level for capability area X?" for three randomly-chosen capability areas. If the answer is "level 5" for all three without further explanation, the practice does not have differentiated target-state planning.

### 4. Read trajectory, not absolute level
A capability area at level 2 last cycle and level 3 this cycle is in a different state than a capability area that has been at level 3 for four consecutive cycles. The first is improving; the second has plateaued. Both score level 3 today, but their architectural significance is opposite — one is a success story to amplify; the other is a stuck programme that needs intervention.

The trajectory dimension is rendered invisible by traditional reporting that publishes the current level only. Effective programmes report the *trajectory line* — the history of levels for each capability area across the last four to six cycles — and read the slope rather than the endpoint. Plateau capabilities are flagged for intervention; declining capabilities trigger urgent review; ascending capabilities are studied to extract transferable lessons.

#### Architectural implications
Trajectory reading requires the assessment process to be stable enough that level changes mean capability changes, not scoring noise. This puts pressure back on Principle 2 (evidence-based scoring) — without evidence-grounding, the trajectory line is dominated by reviewer turnover and morale cycles rather than capability change.

#### Quick test
Look at the most recent maturity report. Does it show a trajectory line per capability area, or only a current level? If only the current level, the practice cannot distinguish ascending from plateau capabilities and treats them identically.

### 5. Calibrate per team rather than enforcing direct cross-team comparison
A capability area scored at level 3 by team A and level 3 by team B does not necessarily mean equivalent capability. The two teams may operate in different domains, with different sub-capability mixtures, and the rubric's level 3 description may apply to different observable behaviours in each. Treating the two scores as directly comparable produces league tables that drive teams toward gaming the rubric — investing in evidence-collection for the questions on the form rather than capability for the actual work.

The discipline is to calibrate per-team — each team has its own assessment cadence, its own assessor, its own evidence base — and use cross-team comparison only at the *trajectory* level. "Team A improved their incident-response from level 2 to level 4 in one year" and "Team B improved theirs from level 3 to level 4 in one year" are comparable trajectories even if the absolute scores are not directly comparable.

#### Architectural implications
The reporting layer must distinguish team-level views (absolute levels matter for the team's own planning) from portfolio-level views (only trajectories aggregate cleanly). Mixing the two — publishing absolute team scores in a portfolio-level view — invites the gaming behaviour above and corrupts the data that the trajectory view depends on.

#### Quick test
If your maturity dashboard shows a side-by-side team comparison of absolute capability levels visible to senior leadership, the architecture has set up gaming pressure. If it shows team trajectories with absolute levels visible only within each team's own view, the architecture is calibrated for honest assessment.

### 6. Run the cadence so each cycle informs the next, not so each cycle produces a number
A maturity assessment that takes a week of effort and produces a five-page report that nobody reads is mature in form and immature in function. The architectural purpose of the assessment is to surface specific capability gaps, prioritise them, and feed them into the next cycle's improvement programme. If the assessment output does not visibly drive the team's quarterly OKRs, capability-investment plan, or hiring decisions, the assessment cycle is decoupled from the rest of the practice and is producing maturity-as-ritual.

A useful assessment ends with three concrete artefacts: (a) the trajectory chart showing per-capability movement since last cycle, (b) the target-state gap analysis showing the largest distance-to-target capabilities, (c) a prioritised investment plan with named owners and timelines for the next cycle. The next cycle then begins with the question: did the planned investments close the gaps they targeted? Cycles where the answer is "no" become the most architecturally important cycles, because they reveal that the assessment-to-improvement loop is broken even if the scores themselves are improving.

#### Architectural implications
The cadence design — annual, semi-annual, quarterly — should be matched to how quickly capability genuinely changes. Quarterly assessments mostly measure noise because real capability does not move that fast. Annual assessments mostly miss intra-year corrections. Semi-annual is often the right default for organisational-capability assessment; quarterly is appropriate only for narrow-scope capability assessments tied to specific improvement programmes.

#### Quick test
At the end of the most recent assessment, was a prioritised investment plan produced with named owners? At the start of the next assessment, was that investment plan reviewed for outcome? If both answers are yes, the assessment-to-improvement loop is closed. If either is no, the cycle is producing reports rather than capability change.

## Five pitfalls

### ⚠️ Composing a private maturity rubric from parts of several published models
The compositing impulse usually originates from a desire to "cover everything." It produces a rubric whose level definitions are inconsistent across capability areas, whose calibration is unvalidated, and whose trajectory line is uninterpretable because every cycle's scores depend on which model fragment dominated which area. The fix is to pick one published model whose scope matches the question being asked, accept the coverage gaps, and use a separate dedicated assessment for areas the chosen model does not cover.

### ⚠️ Scoring on felt maturity rather than artefact evidence
Felt-maturity assessments correlate with team morale, recent incidents, and assessor turnover more than they correlate with capability. A team that just shipped a major release will score themselves higher; a team that just had a production incident will score themselves lower; the actual capability has not changed. The discipline is to require artefact citations for every scored level above baseline. Scores without citations are recorded as low-confidence and excluded from the trajectory line.

### ⚠️ Treating the top level as the universal target
Most capability areas in most organisations should target a mid-level. The top level is for capability areas where the business-of-the-organisation depends critically on that capability. Treating top level as the universal target invests improvement budget evenly across critical and commodity capability, which is the wrong allocation in nearly every case. The fix is the explicit target-state document with rationale per area.

### ⚠️ Reporting current level without trajectory
Current-level-only reporting cannot distinguish ascending from plateau from declining capabilities. It treats them identically. Decision-makers reading current-level reports cannot identify which capabilities are stuck and need intervention. The fix is to publish the trajectory line as the primary view, with current level as a derived secondary number.

### ⚠️ Cross-team comparison of absolute levels visible to leadership
Absolute-level league tables drive teams to game the rubric — collecting evidence for the form rather than building capability for the work. The corrupted evidence-base then makes trajectory reading impossible. The fix is to scope absolute-level visibility to within-team views and surface only trajectories at the portfolio level.

## Maturity assessment readiness checklist

| # | Check | Status |
|---|---|---|
| 1 | A single published maturity model is named as the practice standard | ☐ |
| 2 | The target state per capability area is documented with rationale | ☐ |
| 3 | Evidence-citation requirements are documented for each scoring level | ☐ |
| 4 | The assessment cadence is matched to capability-change rate | ☐ |
| 5 | Trajectory data exists for at least three prior cycles | ☐ |
| 6 | The most recent assessment produced a prioritised investment plan | ☐ |
| 7 | The current cycle reviewed last cycle's investment-plan outcomes | ☐ |
| 8 | Team-level absolute scores are scoped to within-team views only | ☐ |
| 9 | Portfolio-level reporting shows trajectories rather than absolute levels | ☐ |
| 10 | Plateau-flagged capability areas have explicit intervention owners | ☐ |

## Related

- [Maturity Models](../models) — the catalogue of specific maturity models (CMMI, SAMM, DORA, CNCF, AI maturity)
- [Architecture Review Scorecard](../../scorecards/architecture-review) — design-decision-altitude scoring (versus this page's programme-altitude assessment)
- [NFR Scorecard](../../scorecards/nfr) — per-attribute scoring against measurable NFR targets
- [Principles Scorecard](../../scorecards/principles) — adherence scoring against architectural principles
- [Strategy Principles](../../strategy/principles) — meta-strategic principles that frame how strategy operates
- [Governance Scorecards](../../governance/scorecards) — measuring whether governance system is functioning
- [Templates: ADR Template](../../templates/adr-template) — how target-state choices are recorded as decisions
- [Templates: Review Template](../../templates/review-template) — the document format that feeds review scoring
- [Templates: Scorecard Template](../../templates/scorecard-template) — the structural template for scoring artefacts

## References

1. [Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) — *en.wikipedia.org*
2. [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/) — *owaspsamm.org*
3. [DORA — DevOps Research and Assessment](https://dora.dev/) — *dora.dev*
4. [DORA Capabilities Catalog](https://dora.dev/capabilities/) — *dora.dev*
5. [CNCF Cloud Native Maturity Model](https://maturitymodel.cncf.io/) — *maturitymodel.cncf.io*
6. [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) — *aws.amazon.com*
7. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
8. [TOGAF (overview)](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) — *en.wikipedia.org*
9. [ATAM at SEI](https://insights.sei.cmu.edu/library/atam-criteria-evaluation-of-software-and-system-architectures/) — *sei.cmu.edu*
10. [Architecture Tradeoff Analysis Method (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method) — *en.wikipedia.org*
