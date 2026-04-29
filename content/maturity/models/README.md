# Maturity Models

The strategic guide to the catalogue of architecture-relevant maturity models — recognising that the team's awareness of the published landscape rather than reflexive adoption of the first model encountered, the explicit understanding that each model has a *scope* (delivery process, security, DevOps, cloud-native, AI) it covers well and other scopes it does not, the recognition that level structures vary fundamentally across models so cross-model score comparison is meaningless, the appreciation that some models are organisational-altitude and others are system-altitude and they answer different questions, and the awareness that modern architecture practice typically uses two or three models in parallel for different purposes rather than one model for everything are what determine whether the team's choice of maturity instrument matches the question being asked or whether the team mismeasures the wrong dimension because the chosen model was the only one anyone had heard of.

**Section:** `maturity/` | **Subsection:** `models/`
**Alignment:** SEI CMMI | OWASP SAMM | DORA Capabilities | CNCF Cloud Native Maturity | AWS Well-Architected
---

## What "maturity models" means — and why this page is a catalogue rather than a recommendation

A *primitive* approach to maturity modelling is to pick the first published model the team encounters — usually CMMI because it has been around longest, or DORA because it has the most recent buzz — and apply it to everything. The model gets used as a universal instrument for measuring practice quality, even when the model's design intent is much narrower than the question being asked. CMMI was designed to assess software development *process* maturity at organisational scale; applying it to assess a single product team's DevOps capability is a category error. DORA was designed to measure DevOps performance and capability practices at team-of-teams scale; applying it to assess overall architectural practice is also a category error.

The *architectural* alternative is to recognise that the published-maturity-model landscape is a *toolkit*, not a competition. Each model has a scope it was designed for. CMMI fits whole-organisation software-process assessment. SAMM fits secure-development-lifecycle assessment for a security programme. DORA fits team-and-organisation DevOps capability assessment. CNCF Cloud Native fits cloud-native-platform-adoption journey assessment. AI-readiness models fit AI-engineering-capability assessment for organisations introducing AI workloads. A mature architecture practice typically uses two or three of these in parallel, each scoped to its design intent, with deliberately separate trajectory lines and deliberately no aggregation of scores across them.

This page is a *catalogue* and a *selection guide*, not a recommendation. The guidelines for using whichever model you select live in [`maturity/guidelines`](../guidelines).

## How maturity models compare on what they cover

| Model | Primary scope | Levels | Altitude | Best fit |
|---|---|---|---|---|
| **CMMI** | Software development process maturity | 5 (Initial → Optimising) | Organisation | Whole-organisation process maturity, regulated industries |
| **OWASP SAMM** | Secure development lifecycle | 3 per practice (1, 2, 3) | Programme | Security-engineering programme assessment |
| **DORA Capabilities** | DevOps capabilities and outcomes | Continuous (capability presence + outcome metrics) | Team / org | Delivery performance and DevOps capability investment |
| **CNCF Cloud Native** | Cloud-native platform adoption | 5 (Build → Operate → Scale → Improve → Optimise) | Programme | Cloud-native transformation journey |
| **AWS Well-Architected** | Cloud workload quality (six pillars) | Per-question high/medium/low risk | System | Per-workload review, AWS context |
| **AI maturity (various)** | AI-engineering capability | Varies (typically 4–5) | Organisation / Programme | AI/ML capability buildout |

The columns matter more than the rows. *Scope* is what the model was designed to measure; *levels* describes the structure of the scoring; *altitude* answers "is this for one team, one programme, or the whole organisation?"; *best fit* names the question this model is good at answering.

## Six principles for choosing among models

### 1. Match the model's scope to the question being asked
The question "how good is our delivery practice?" maps to DORA. The question "how mature is our secure-development programme?" maps to SAMM. The question "how far along is our cloud-native adoption journey?" maps to CNCF. Asking DORA to answer "how mature is our security programme?" is a category error — DORA does not have the resolution to distinguish security-engineering practices that SAMM was designed to measure. Ask the question first, *then* select the model.

#### Architectural implications
Matching scope to question prevents the most common maturity-modelling failure: using a generic model to answer a specific question and getting a generic answer. The selection happens at the moment the practice decides what it is trying to learn. The model is the instrument, not the inquiry.

#### Quick test
Look at the most recent maturity assessment. Read the conclusions. Is the question being answered the question the chosen model was designed to answer? If the model says "process" and the conclusions say "security programme readiness," the scope-question match is broken.

### 2. Treat altitude as a binding constraint, not an adjustable parameter
CMMI is an organisation-altitude model. It assumes the assessment unit is the organisation or a major business unit. It does not produce sensible per-team scores. SAMM is a programme-altitude model — the assessment unit is the security programme, not individual teams. AWS Well-Architected is a system-altitude model — the assessment unit is a single workload, not the team or the programme. Crossing altitudes — using CMMI per team, or using Well-Architected for organisational policy assessment — produces results that look numerical but are meaningless because the rubric was designed for a different unit-of-assessment.

#### Architectural implications
The altitude constraint maps directly to who the assessment audience is: organisation-altitude assessments speak to senior leadership; programme-altitude to programme owners; system-altitude to the workload-owning team. Choosing the wrong altitude produces an assessment whose audience cannot act on the findings.

#### Quick test
For a recent assessment, ask: who is the intended audience for the findings, and what decisions will they make based on the result? If the audience is a single product team and the model is CMMI, the altitude is mismatched. If the audience is the CISO and the model is AWS Well-Architected, the altitude is also mismatched.

### 3. Use multiple models in parallel for different scopes; never aggregate scores across them
A mature practice typically uses two or three models in parallel. A regulated organisation might use CMMI for process maturity (annual, organisation-altitude), SAMM for security programme (semi-annual, programme-altitude), and Well-Architected for major workloads (per-major-release, system-altitude). Each runs on its own cadence, each produces its own trajectory line, and the trajectories are reported separately. The temptation to combine them into a "composite maturity score" is consistently wrong: the level definitions are not comparable, the scoring scales are not comparable, and the aggregation has no validated weighting. The composite is meaningful-looking but uninterpretable.

#### Architectural implications
The reporting layer must keep the per-model trajectories visibly separate. The senior architecture practice reads each trajectory in its own context — DORA tells the delivery story, SAMM tells the security story, Well-Architected tells the workload story — and synthesises across them in narrative rather than in numbers.

#### Quick test
Look at the maturity dashboard. Is there a single number labelled "overall architecture maturity"? If so, it is almost certainly a composite of incompatible models and should be removed.

### 4. Recognise level-structure differences as architecturally significant
CMMI has five named levels with explicit descriptions (Initial, Managed, Defined, Quantitatively Managed, Optimising). SAMM has three levels per practice. DORA has no fixed levels — it has capabilities you either have or don't and outcome metrics on continuous scales. CNCF has five named levels of a journey (Build, Operate, Scale, Improve, Optimise). AWS Well-Architected has no levels — it has questions answered with high/medium/low risk identification.

These structural differences are not cosmetic. CMMI's five levels embed an assumption that maturity progresses through specific named transitions. DORA's continuous scales embed the assumption that capability is dimensional rather than staged. The structure tells you what the model believes about how capability develops. Choosing a model means accepting its structural model of capability development.

#### Architectural implications
A team that believes capability progresses in named stages should pick CMMI or CNCF — the structure matches the belief. A team that believes capability is dimensional and should be measured by outcomes should pick DORA — the structure matches that belief. Mismatch produces an assessment whose results are filtered through a structure the assessors do not actually believe in, which corrupts the scoring discipline.

#### Quick test
Ask the architecture practice whether they believe capability progresses through named levels (Initial → Defined → Optimising) or whether they believe capability is dimensional (more practices, better outcomes). Then check whether the chosen model's structure matches that belief.

### 5. Account for evidence-collection cost in the cadence
SAMM scoring requires evidence per security practice, often spread across multiple teams, often requiring interviews to clarify what is implemented and where. DORA scoring requires telemetry — deployment frequency, change failure rate, lead time, MTTR — that the organisation must already be collecting. AWS Well-Architected scoring requires workload-owner availability for several hours of structured review. The evidence-collection cost varies by an order of magnitude across models.

A model with high evidence-collection cost run too frequently produces assessment fatigue and gradual quality decline; the same model run on an appropriate cadence produces sustainable trajectory readability. CMMI assessments at organisational altitude are typically annual or two-yearly. SAMM at programme altitude is typically semi-annual. DORA, when telemetry is automated, can be continuous — the cost is in the telemetry pipeline, not in the assessment event.

#### Architectural implications
Cadence selection is a cost-of-evidence calculation, not just a "how often do we want a number" calculation. The cadence should be the slowest one that still produces actionable trajectory readings. Faster cadences than that produce noise dressed as signal.

#### Quick test
For a chosen model, calculate the person-hours required per assessment cycle. Multiply by the cadence. If the resulting annual person-hours exceed a few percent of the practice's total time, the cadence is probably too fast for the model's evidence-collection cost.

### 6. Anticipate model evolution; pin the version assessed against
CMMI has had multiple major revisions (CMMI v1.3, CMMI v2.0, CMMI v3.0). SAMM has had revisions (SAMM 1.0, SAMM 2.0). DORA's capabilities catalogue evolves yearly. AWS Well-Architected adds new lenses regularly and revises pillar questions. An assessment against "CMMI" without specifying which version is ambiguous; the trajectory line across versions is uninterpretable because level definitions changed.

The discipline is to record the exact model version against which each assessment was run, and to schedule version-migration as a deliberate one-time event with a documented mapping from old levels to new. The cycle in which migration occurs is flagged as a transition cycle whose trajectory data is interpretable only against the new version forward.

#### Architectural implications
Version pinning aligns maturity assessment with the rest of the practice's reproducibility discipline. ADRs are version-controlled; design templates are version-controlled; assessment instruments should be too. Without versioning, the historical trajectory becomes uninterpretable as the underlying model evolves.

#### Quick test
Look at the maturity report. Is the model version cited? If it says "CMMI" or "SAMM" without a version number, the practice is not pinning, and the trajectory line crosses version boundaries with no explicit mapping.

## Five pitfalls

### ⚠️ Picking the most-cited model rather than the model whose scope matches the question
DORA is currently the most-cited DevOps maturity reference. SAMM is the most-cited security maturity reference. CMMI is the most-cited general process maturity reference. The most-cited model in a domain is the one most likely to be picked reflexively. Reflexive selection skips the step where the team asks "what question are we trying to answer?" and produces an assessment whose results may not address that question. The fix is the explicit question-first selection: write the question down, then pick the model whose design intent matches.

### ⚠️ Aggregating scores across models into a "composite maturity score"
The composite is uninterpretable because level definitions, scoring scales, and capability-area decompositions differ across models. The composite looks scientific because it produces a number; it is not. Stakeholders reading the composite cannot infer anything actionable from a one-point change. The fix is to keep per-model trajectories visibly separate and synthesise across them in narrative rather than numbers.

### ⚠️ Using a system-altitude model for organisation-altitude questions (or the reverse)
AWS Well-Architected results across many workloads cannot be averaged into "how good is our cloud architecture practice" — that is an organisation-altitude question that needs an organisation-altitude instrument. CMMI results cannot be subdivided into "how mature is each team's process" — CMMI's unit-of-assessment is the organisation. The fix is to honour altitude as a binding constraint and pick a model designed for the altitude of the question.

### ⚠️ Running maturity assessments at a cadence faster than capability genuinely changes
Most architectural capability does not change quarterly. Quarterly assessments measure mostly noise — assessor turnover, evidence-collection variability, recent-incident salience — rather than capability change. The trajectory line becomes a random walk whose movement is uncorrelated with real capability movement. The fix is to match cadence to capability-change rate; semi-annual to annual is appropriate for most organisational-altitude assessments.

### ⚠️ Failing to pin the model version assessed against
Model versions evolve. CMMI 1.3 → 2.0 → 3.0 changed level definitions; SAMM 1.0 → 2.0 changed practice structures. An assessment trajectory that crosses a version boundary without explicit migration treatment is uninterpretable: a level 3 in v1.3 is not the same as a level 3 in v2.0. The fix is to record the version with the assessment and treat version migration as a deliberate transition cycle with documented level mapping.

## Maturity model selection checklist

| # | Check | Status |
|---|---|---|
| 1 | The question being asked is documented before model selection | ☐ |
| 2 | The model's design-intent scope matches the question being asked | ☐ |
| 3 | The model's altitude (system / programme / organisation) matches the audience | ☐ |
| 4 | The model's level structure (named levels / continuous scales / risk levels) matches the practice's belief about capability development | ☐ |
| 5 | Evidence-collection cost has been estimated and the cadence calibrated against it | ☐ |
| 6 | The model version is recorded with each assessment cycle | ☐ |
| 7 | If multiple models are in use, their scopes do not overlap on the same question | ☐ |
| 8 | No aggregation across models into a composite score is being done | ☐ |
| 9 | Per-model trajectory lines are reported separately at portfolio level | ☐ |
| 10 | A version-migration plan exists for each adopted model | ☐ |

## Related

- [Maturity Guidelines](../guidelines) — how to use whichever model is selected; the protocol around the instrument
- [DORA — DevOps capabilities and outcomes](https://dora.dev/) — referenced in DevOps maturity assessment
- [Architecture Review Scorecard](../../scorecards/architecture-review) — design-decision-altitude scoring (versus this page's organisation-altitude questions)
- [NFR Scorecard](../../scorecards/nfr) — per-attribute scoring against measurable NFR targets
- [Strategy Principles](../../strategy/principles) — meta-strategic principles that frame strategic choices
- [Strategy: AI Readiness](../../strategy/ai-readiness) — framework for AI-engineering capability buildout
- [Governance Scorecards](../../governance/scorecards) — measuring whether the governance system itself is functioning
- [Templates: Scorecard Template](../../templates/scorecard-template) — the structural template for scoring artefacts

## References

1. [Capability Maturity Model Integration (CMMI)](https://en.wikipedia.org/wiki/Capability_Maturity_Model_Integration) — *en.wikipedia.org*
2. [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/) — *owaspsamm.org*
3. [DORA — DevOps Research and Assessment](https://dora.dev/) — *dora.dev*
4. [DORA Capabilities Catalog](https://dora.dev/capabilities/) — *dora.dev*
5. [CNCF Cloud Native Maturity Model](https://maturitymodel.cncf.io/) — *maturitymodel.cncf.io*
6. [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) — *aws.amazon.com*
7. [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/) — *learn.microsoft.com*
8. [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework) — *cloud.google.com*
9. [TOGAF (overview)](https://en.wikipedia.org/wiki/The_Open_Group_Architecture_Framework) — *en.wikipedia.org*
10. [Continuous Architecture in Practice](https://www.oreilly.com/library/view/continuous-architecture-in/9780136523710/) — *oreilly.com*
