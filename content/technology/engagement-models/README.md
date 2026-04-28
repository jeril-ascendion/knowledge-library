# Engagement Models

**Strategic Delivery Frameworks — aligning collaborative models and AI-native workflows to your goals.** The technology decisions get the attention; the engagement model determines whether the technology gets delivered. This page describes how we structure partnerships — from staff augmentation through managed services to AI-native delivery — and the principles that make each tier work.

**Section:** `technology/` | **Subsection:** `engagement-models/`
**Alignment:** SAFe | Lean Software Development | Outcomes-Based Contracting | GitOps

---

## What "engagement models" actually means

How a delivery partnership is structured determines almost everything that happens within it: who owns the backlog, who bears the risk if outcomes slip, how value is measured, who escalates when something goes wrong, what the path looks like when the engagement matures. In our experience across hundreds of engagements, the single biggest predictor of success is not the technology stack, the team size, or the budget — it is the *clarity of accountability*. Who owns what. Who bears what risk. How value is measured.

This page describes our framework not as a sales pitch for a particular model, but as a diagnostic. By the end, you should have a shared language for where you are today and where you want to go.

---

## Six principles

### 1. Accountability clarity is the strongest predictor of engagement success

Every engagement has a Responsibility–Risk pair. *Responsibility* is what each party does — sourcing, governing, delivering, accepting. *Risk* is who bears the cost when something goes wrong — missed deadlines, scope creep, quality issues, retention, ramp-down. The cleanest engagements have these mapped explicitly: client owns A, partner owns B, the boundary between them is sharp and rehearsed. The most painful engagements have ambiguity at the boundary — both parties assumed the other was handling something, and the gap surfaces during a real problem.

#### Architectural implications

- The engagement model is documented with an explicit Responsibility–Risk matrix; both parties review and agree before kickoff.
- The boundary is exercised in dry-run scenarios (a missed milestone, a scope-change request, a resource departure) so the response is rehearsed, not improvised.
- Escalation paths and decision rights are explicit: who decides on scope, who decides on staffing, who decides on outcomes acceptance.

#### Reference

The principle parallels [Deming's articulation](https://en.wikipedia.org/wiki/W._Edwards_Deming) of clear ownership in quality management — a system without clear accountability cannot be improved because no one owns improvement.

---

### 2. Three tiers — Staffing, Managed Capacity, Managed Services — fit three different needs

The framework has three tiers, each appropriate for different organisational situations. *Staffing & Resource Augmentation* — engineers embedded in your team under your governance — fits when you have strong internal delivery leadership, defined backlogs, and need to scale capacity without permanent headcount. *Managed Capacity* — a governed delivery unit with a Service Delivery Lead, accountable for KPIs tied to outcomes — fits when you want delivery accountability without surrendering architectural ownership. *Managed Services* — end-to-end solution ownership with partner-driven governance — fits when you have a defined outcome and want a partner accountable for it. Picking the right tier requires honest assessment of where you are; over-buying complicates engagements unnecessarily, under-buying leaves accountability gaps.

#### Architectural implications

- Staffing tier: Ascendion handles sourcing, screening, payroll, compliance, ramp-up/ramp-down; client owns delivery, governance, and outcomes.
- Managed Capacity tier: Ascendion adds a Service Delivery Lead, KPI-aligned governance, upskilling and cross-skilling investment in placed engineers, delivery accountability.
- Managed Services tier: Ascendion takes end-to-end solution ownership with partner-driven governance, embedded quality engineering, and proactive surfacing of risks.
- The right tier matches the client's internal delivery maturity and risk tolerance — not the firm's preferred selling motion.

#### Reference

The tiering parallels the [SAFe Configurations](https://framework.scaledagile.com/) — not because the framework's specifics apply, but because the *idea* of selecting the right operating model for the organisation's actual situation is foundational to delivery success.

---

### 3. The maturity arrow is earned, not promised

Most mature engagements move along a trajectory: Staffing → Managed Capacity → Managed Services. The trajectory exists not because we want clients to spend more, but because trust is built over engagements. A client sees how we deliver, how we govern, how our people perform under pressure — and that observed track record is what justifies handing over more accountability. The arrow is not a sales tactic; it is a description of how trust between organisations gets built. Engagements that try to start at Managed Services without the relationship history typically struggle, because both parties are still learning each other when they should be operating.

#### Architectural implications

- The right starting tier is the one that matches current trust and current organisational maturity, not the most ambitious one.
- Progression toward higher tiers is informed by demonstrated outcomes — KPI achievement, governance quality, the way escalations were handled — not by calendar time.
- Transitions between tiers are deliberate engagements in themselves, with documented changes in responsibility, governance, and KPIs.

#### Reference

[Charles Handy — The Empty Raincoat](https://en.wikipedia.org/wiki/Charles_Handy) and the broader literature on outsourcing maturity models — articulating how partnership trust progresses through demonstrated outcomes, not through commercial commitment.

---

### 4. KPI alignment trades hours for outcomes

In Staffing tier, the natural KPI is hours — engineers placed, hours billed. This is the right metric for that tier because Ascendion's accountability is the placement, not the outcome. In Managed Capacity and above, hours become misleading: the question that matters is "are deliverables landing on time, are outcomes hitting the targets we jointly defined, is the transition to steady state seamless?" Aligning KPIs to outcomes — even where the contract is on T&M — changes how the team operates, because it pulls focus toward the things clients actually want, not the things engineering hours measure.

#### Architectural implications

- Each tier has KPIs appropriate to its accountability — hours for Staffing, deliverables and SLA-aligned governance for Managed Capacity, outcomes for Managed Services.
- KPIs are agreed before engagement start, reviewed in cadence, and tied to escalation criteria when missed.
- The contract vehicle (T&M, Fixed Price, Milestones-based, Outcomes-based) is chosen to support the KPIs, not to obscure them.

#### Reference

The contracting vehicles trace to [Performance-Based Contracting (Outcomes-Based Contracting)](https://en.wikipedia.org/wiki/Performance-based_contracting) — a procurement discipline that aligns commercial incentive with delivery results rather than effort.

---

### 5. AI-native delivery via AAVA accelerates without replacing engineering judgment

AAVA is our AI-native delivery model — a multi-agent framework that augments human engineers across the lifecycle. Discovery agents extract requirements from existing artefacts; design agents generate architectural options; coding agents produce implementations under human review; testing agents generate and execute test suites; documentation agents keep specs current. The discipline that makes this productive rather than chaotic is the *human accountability* — agents accelerate the work; humans approve the outputs, hold the architectural judgment, and own the integration. Done well, AAVA compresses cycle times by 2–4x without reducing quality. Done poorly — agents generating volumes of work without human review — it produces fast unreviewable output.

#### Architectural implications

- Agent outputs flow through human review gates appropriate to risk — code reviews, architecture sign-offs, design approvals.
- Agent activity is logged and observable; the team knows what the agents did, what they didn't do, and what humans changed.
- Agent capabilities evolve continuously; the framework's value compounds with usage as patterns and prompts mature.
- The team's engineering judgment remains the architecture's source of truth — agents are tools, not architects.

#### Reference

The pattern parallels the broader literature on [AI-augmented software engineering](https://research.google/pubs/?team=PA) — productive use depends on integrating agents into existing engineering workflows rather than treating them as autonomous replacements.

---

### 6. Seamless transition to steady-state is the engagement's last mile

The most commonly botched part of any engagement is the transition out — when the project moves to operational steady state and the client team takes over. Sloppy transitions leave the client team without the knowledge they need; over-engineered transitions stretch the engagement uselessly while the team is already on next things. The discipline is operationalising the transition: knowledge transfer plans documented before delivery completes, runbooks written and exercised, on-call rotations dual-staffed with handover, retrospectives including the receiving team. Clients consistently tell us the transition was painful with prior vendors — and our investment in making it not painful is part of the difference.

#### Architectural implications

- Transition planning begins at engagement start, not at engagement end.
- Documentation, runbooks, and operational know-how are deliverables, not byproducts; they are reviewed and exercised before handover.
- The receiving team is involved in the engagement's later phases — pair operations, shadow on-call — so they own the system before formal handover.
- The transition has its own success criteria: the receiving team can operate independently, has resolved at least one real incident, and reports confidence rather than concerns.

#### Reference

The discipline is articulated in [ITIL Service Transition](https://www.axelos.com/certifications/itil-service-management) — the canonical reference for moving services from project delivery to operational steady state, with the disciplines (transition planning, knowledge management, change management) that make it survivable.

---

## Architecture Diagram

The diagram below shows the three-tier engagement framework with the maturity arrow, the four engagement vehicles (Time & Materials, Fixed Price, Milestones-based, Outcomes-based) appropriate to each tier, and the AAVA AI-native delivery model that augments engineering across all tiers.

---

## Common pitfalls

### ⚠️ Buying outcomes when you need capacity

A client whose internal delivery leadership is strong but is short on capacity buys a Managed Services engagement. The partner takes ownership of decisions the client wanted to retain; the engagement struggles because the model doesn't match the actual need.

#### What to do instead

Match the tier to the actual need, not to perceived sophistication. Strong internal leadership + capacity gap = Staffing or Managed Capacity. Weak internal leadership + clear outcome target = Managed Services. The honest assessment matters more than the impressive label.

---

### ⚠️ Buying capacity when you need outcomes

A client with no delivery leadership buys staffing. Engineers arrive without governance; outcomes drift; the engagement consumes effort without producing value, and the client's frustration grows.

#### What to do instead

Recognise that staffing requires internal delivery leadership to translate engineers into outcomes. Without that leadership, Managed Capacity or Managed Services is the appropriate model — accept the cost in exchange for outcome accountability.

---

### ⚠️ KPIs measuring effort, not outcome

The engagement is on T&M, the partner reports hours billed weekly, both parties feel productive. Six months in, the client realises they have a lot of effort consumed and unclear outcomes. The KPI structure rewarded effort, so effort is what arrived.

#### What to do instead

Even on T&M, the KPIs measure outcomes. Deliverables landing on time, quality bars met, milestones reached. Hours are tracked; outcomes are evaluated. The conversation in steering committees is about the latter, not the former.

---

### ⚠️ AAVA used as a magnifier of unreviewed work

AI agents produce code, tests, and documentation faster than humans can review thoroughly. Reviews become rubber stamps; quality issues sneak through; the volume of work obscures the issues until production reveals them.

#### What to do instead

Human review gates appropriate to risk. The acceleration target is meaningful work shipped, not raw artefacts produced. AAVA's value comes from compressing cycle time on well-understood work, not from bypassing engineering judgment on novel work.

---

### ⚠️ Transition as project closure

The engagement ends; documentation is hastily written; the receiving team gets a knowledge-transfer session and a wiki link. The first incident reveals what wasn't transferred; the receiving team escalates back to the partner repeatedly; the engagement informally extends because the formal end didn't actually end it.

#### What to do instead

Transition planned from kickoff, exercised before formal completion, validated by the receiving team operating autonomously. The engagement closes when transition is verified, not when the original scope is delivered.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | The engagement model is documented with an explicit Responsibility–Risk matrix ‖ Both parties have agreed who owns what and who bears risk for what; the boundary is sharp; ambiguity is recognised as a problem to fix before kickoff, not a detail to handle later. | ☐ |
| 2 | The chosen tier matches the client's actual delivery maturity and risk tolerance ‖ Honest assessment of internal leadership, backlog clarity, and risk appetite drives the choice; over-buying is recognised as expensive theatre, under-buying is recognised as accountability gap. | ☐ |
| 3 | The contracting vehicle (T&M, Fixed Price, Milestones, Outcomes) supports the KPIs ‖ The vehicle reinforces the engagement's intent rather than obscuring it; T&M for discovery and evolving scope, Fixed Price for stable scope, Milestones for checkpointed delivery, Outcomes for mature partnerships. | ☐ |
| 4 | KPIs measure outcomes, not effort ‖ Even on hourly contracts, the steering conversation is about deliverables landing, quality met, transition viable; hours are tracked, outcomes are evaluated. | ☐ |
| 5 | A Service Delivery Lead is assigned for Managed Capacity and Managed Services tiers ‖ Single accountable point on the partner side; owns governance, KPI tracking, and proactive escalation; the client always has someone to ask. | ☐ |
| 6 | Upskilling and cross-skilling of placed engineers is invested in deliberately ‖ The team that arrives at month one is the team that arrives at month twelve, evolved with the stack; engineer growth is part of the engagement's value, not a hiring concern absorbed silently. | ☐ |
| 7 | AAVA usage has documented review gates appropriate to risk ‖ AI agents accelerate; humans review and judge; the engineering quality bar is held by humans, with AAVA compressing the work needed to meet it rather than bypassing the standard. | ☐ |
| 8 | Transition planning begins at engagement kickoff, not at delivery completion ‖ Documentation, runbooks, and operational know-how are deliverables; the receiving team is involved in later phases; transition success criteria are documented and verified. | ☐ |
| 9 | Escalation paths are explicit, exercised, and trusted by both parties ‖ When something goes wrong, the path is rehearsed; both parties know who calls whom; the response is calibrated, not chaotic. | ☐ |
| 10 | The engagement has a documented progression path through the maturity arrow ‖ The trajectory from current tier to the next is named, with the conditions (trust, demonstrated outcomes, evolved scope) that would justify progression; the partnership is going somewhere, not parked. | ☐ |

---

## Related

[`technology/practice-circles`](../practice-circles) | [`technology/devops`](../devops) | [`principles/foundational`](../../principles/foundational) | [`principles/modernization`](../../principles/modernization) | [`patterns/deployment`](../../patterns/deployment) | [`technology/api-backend`](../api-backend)

---

## References

1. [SAFe Framework](https://framework.scaledagile.com/) — *scaledagile.com*
2. [Lean Software Development](https://en.wikipedia.org/wiki/Lean_software_development) — *Wikipedia*
3. [Performance-Based Contracting](https://en.wikipedia.org/wiki/Performance-based_contracting) — *Wikipedia*
4. [ITIL Service Transition](https://www.axelos.com/certifications/itil-service-management) — *axelos.com*
5. [W. Edwards Deming](https://en.wikipedia.org/wiki/W._Edwards_Deming) — *Wikipedia*
6. [Charles Handy — The Empty Raincoat](https://en.wikipedia.org/wiki/Charles_Handy) — *Wikipedia*
7. [Project Management Institute](https://www.pmi.org/) — *pmi.org*
8. [Agile Manifesto](https://agilemanifesto.org/) — *agilemanifesto.org*
9. [Open Group — Service Integration and Management](https://www.opengroup.org/) — *opengroup.org*
10. [Kotter — Leading Change](https://www.kotterinc.com/methodology/8-steps/) — *kotterinc.com*
