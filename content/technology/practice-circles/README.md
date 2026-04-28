# Practice Circles

**Specialized Domains — focused centers of excellence for enterprise integration and modernization.** Engineering excellence at scale requires depth, and depth requires deliberate cultivation. Practice circles are how Ascendion organises that depth — communities of practitioners with shared craft, tooling, methodologies, and accountability for outcomes in their domain. This page describes four circles — Platform, Enterprise, COTS, and Legacy Modernization — and the principles that make each effective.

**Section:** `technology/` | **Subsection:** `practice-circles/`
**Alignment:** Salesforce | MuleSoft | Microsoft Power Platform | Apache Kafka

---

## What "practice circles" actually means

A practice circle is not an org-chart box. It is a *community of practice* — a group of engineers who share a craft, deliberately develop their depth in it, hold each other accountable for quality in that domain, and pollinate the rest of the organisation with what they've learned. The practice exists across project boundaries; engineers join projects from circles, return to circles between engagements, and bring back learnings that feed the circle's playbooks. The model recognises that deep expertise — Salesforce platform architecture, mainframe modernisation, MuleSoft integration patterns, Power Platform governance — cannot be built from generalist staffing alone. It has to be cultivated.

We organise around four circles, each with its own depth, tooling, and accountability. The circles cross-pollinate by design: a complex engagement typically draws from multiple circles, and the integration of their work is itself a practice the circles develop together.

---

## Six principles

### 1. A practice is a community of practice, not an org-chart box

The thing that distinguishes a practice circle from a department is the *practice* itself: the shared body of knowledge, the playbooks that capture hard-won lessons, the quality bars members hold each other to, the mentorship and craft development. A department has a manager and a budget; a practice has a craft. Treating practices as departments produces administrative units; treating them as communities of practice produces depth that compounds. The implementation difference is small but consequential — practitioners spend time in the circle (knowledge-sharing, internal projects, certifications), not just on client work, and the time is budgeted as part of the practice's investment in itself.

#### Architectural implications

- Each circle has its own playbooks, reference implementations, and quality bars maintained by the circle, not handed down by management.
- Circle time is budgeted alongside billable time — sustained depth requires deliberate investment, not heroics from individuals on weekends.
- Senior practitioners mentor juniors as part of the role, not as a side project; the circle's continuity depends on it.

#### Reference

[Etienne Wenger — Communities of Practice](https://www.wenger-trayner.com/introduction-to-communities-of-practice/) — the foundational treatment of how craft develops in groups that share a domain, distinct from how teams operate within reporting structures.

---

### 2. The Platform Circle owns delivery excellence as a discipline

The Platform Circle is the home for application development excellence — the patterns, tooling, methodologies, and value propositions that scale across every engagement. It is where reusable accelerators live (component libraries, scaffolds, reference architectures), where the firm's methodology is curated (BMAD-style agentic delivery, AI-augmented engineering, agile-at-scale patterns), and where the conversation about *how we deliver* happens before any specific client engagement begins. The circle's outputs are the patterns that make every other circle's work faster and more consistent.

#### Architectural implications

- Reference architectures and accelerators are versioned, documented, and stewarded by the Platform Circle — not informally maintained by whoever started them.
- Methodology evolves continuously — agentic delivery, AI-augmented coding, cloud-native engineering practices — and is reflected in the patterns the firm offers.
- Cross-project learnings (what worked, what didn't, what we'd do differently) flow back to the circle and update the playbooks.

#### Reference

The discipline parallels the [SEI's CMMI](https://cmmiinstitute.com/) and modern Agile Centre of Excellence patterns — the formal articulation of delivery excellence as a stewarded organisational asset rather than a tribal one.

---

### 3. The Enterprise Circle integrates the systems clients already operate

Most enterprises do not start from zero. They have Salesforce for sales, ERP for finance, a data platform for analytics, message brokers (Kafka) for inter-system integration, and decades of investment in these platforms. The Enterprise Circle is the home for deep expertise in these systems — how to extend Salesforce without painting into a corner, how to design MuleSoft integrations that survive change, how to build Kafka topologies that scale, how to architect data platforms that serve both operational and analytical workloads. Engagements that touch enterprise integration succeed when this depth is brought from the start, not when it is improvised.

#### Architectural implications

- Salesforce, MuleSoft, Kafka, and data-platform expertise are sustained as deep specialisms — not "we have a few engineers who've used it."
- Integration patterns (Canonical Data Models, API gateways, event meshes, ETL/ELT pipelines) are documented and reusable across engagements.
- Vendor relationships, certification levels, and partner programmes are maintained by the circle — the firm's standing with platform vendors is part of the value to clients.

#### Reference

[Salesforce — Architect Resources](https://architect.salesforce.com/), [MuleSoft — Anypoint Platform](https://www.mulesoft.com/platform/api), [Apache Kafka](https://kafka.apache.org/) — the canonical references for the platforms the Enterprise Circle specialises in.

---

### 4. The COTS Circle treats commercial software as a programming surface

Power BI, Tableau, Power Automate, Microsoft Fabric, and the broader Power Platform are commercial products with point-and-click interfaces — and that surface is precisely what creates the trap. Treated as configuration tools, these platforms accumulate brittle workflows that no one understands, that fail on edge cases, that cannot be tested in CI, that do not version cleanly. Treated as a *programming surface* — with the same engineering discipline applied to enterprise code — they become a high-leverage way to deliver business intelligence, automation, and analytics at speed. The COTS Circle is the home for the engineering discipline that makes these platforms enterprise-grade rather than tactical.

#### Architectural implications

- Power BI semantic models, Power Automate flows, and Fabric data pipelines are versioned, reviewed, and tested — not built once and abandoned.
- Reusable patterns (parameterised reports, branded templates, shared connectors) are stewarded centrally so each project doesn't reinvent them.
- Governance — who can publish, what data sources are sanctioned, how DLP policies apply — is part of the architecture, not an afterthought.

#### Reference

[Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/) and [Microsoft Power Platform — Centre of Excellence Starter Kit](https://learn.microsoft.com/en-us/power-platform/guidance/coe/starter-kit) — the canonical references for treating these platforms as engineering surfaces with proper governance.

---

### 5. Legacy modernization is a knowledge problem, not a technology problem

The hardest part of modernising a mainframe COBOL system, an Oracle Forms application, or a thirty-year-old VB6 codebase is not the target stack. It is recovering the knowledge that was once present in the team that built the original — the business rules, the integration touch-points, the failure modes, the workarounds that compensate for issues no one remembers. Modernisation projects that focus on the technology (rewrite in Java! migrate to AWS!) without solving the knowledge problem produce systems that work in the demo and fail in production because the recovered behaviour is incomplete. The Legacy Modernization Circle's central commitment is the *knowledge* discipline — extracting, documenting, and validating the implicit logic of legacy systems before rewriting them.

#### Architectural implications

- Knowledge extraction (interviewing remaining experts, mining COBOL/PL/SQL/forms code, instrumenting legacy systems for behaviour observation) is the first phase, not an afterthought.
- The strangler-fig pattern — incrementally replacing legacy capabilities while the legacy system continues to run — is the default approach; big-bang rewrites are recognised as the high-risk option they are.
- Validation — the new system produces the same outputs as the legacy system for known inputs — is a continuous activity, not a final UAT.

#### Reference

The discipline draws from [Michael Feathers — Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/), and Sam Newman's [strangler-fig migration patterns](https://martinfowler.com/bliki/StranglerFigApplication.html), which together articulate why legacy is a knowledge problem first and a technology problem second.

---

### 6. Circles cross-pollinate by design

A complex engagement rarely lives in one circle. A digital transformation might draw from Platform (the methodology), Enterprise (Salesforce + Kafka + MuleSoft), COTS (Power BI for executive dashboards), and Legacy (the systems being replaced). Letting these contributions silo produces an engagement where each part is excellent and the whole is fragmented. Designing for cross-pollination — engagement leads who span circles, shared playbooks for inter-circle handoffs, retrospectives that include all four circles — produces engagements where the integration is itself part of the value delivered.

#### Architectural implications

- Engagement teams are deliberately staffed across circles; an engagement lead has the relationships and the authority to draw from each.
- Inter-circle handoff patterns (how Platform engineers integrate with Salesforce work, how Legacy integrates with new microservices) are documented and tested in reference engagements before client work.
- Retrospectives include all circles that touched the engagement; learnings flow back to each circle's playbooks.

#### Reference

The cross-pollination discipline parallels the [Spotify Guild model](https://blog.crisp.se/wp-content/uploads/2012/11/SpotifyScaling.pdf) — the well-known articulation of how chapters and guilds enable depth and cross-cutting knowledge sharing simultaneously.

---

## Architecture Diagram

The diagram below shows the four practice circles as distinct centres of expertise, with cross-pollination flows between them, drawing from a shared platform foundation (methodology, accelerators, AI-native delivery patterns) and converging on client engagements.

---

## Common pitfalls

### ⚠️ Practice as cost centre

The practice is treated as overhead — time spent in the practice is non-billable, so individuals are pressured to minimise it. The practice's depth erodes; playbooks fall behind; the firm is left selling a brand without a craft.

#### What to do instead

Practice time is part of the role, budgeted into capacity planning, evaluated as part of practitioner growth. Mature firms treat practice investment as a strategic asset, not a cost line.

---

### ⚠️ Generalist staffing for specialised work

Engagements that need deep Salesforce, mainframe, or platform expertise are staffed with generalists "with some experience in X." The work happens, but slowly, with workarounds that compound, with quality the specialist would have caught.

#### What to do instead

Engagements requiring specialist depth pull from the relevant circle. The cost is real; the alternative — generalist staffing producing fragile work — is more expensive in the long run.

---

### ⚠️ COTS as configuration

Power Platform, Salesforce, and Tableau are treated as point-and-click tools. Workflows accumulate without engineering discipline; nothing is versioned, tested, or reviewable; failure modes accumulate invisibly.

#### What to do instead

The COTS Circle applies engineering discipline to these platforms — version control, code review, automated testing where possible, governance frameworks. The platforms remain accessible to citizen developers; the enterprise-grade work happens with engineering rigor.

---

### ⚠️ Legacy modernisation by rewrite

The legacy system is dismissed as obsolete and rewritten in a modern stack with insufficient understanding of the existing behaviour. The new system passes its tests; production users report dozens of edge cases the rewrite doesn't handle. Six months in, the team is back-porting legacy logic into the new system.

#### What to do instead

Knowledge extraction first, strangler-fig migration second. The new system runs alongside the legacy until its behaviour is validated for the actual production input distribution. Big-bang cutover is the rare exception, not the default.

---

### ⚠️ Circles in silos

Each circle does excellent work in its own domain and hands off without integration. The client experiences seams; the engagement loses the value of having drawn from multiple circles in the first place.

#### What to do instead

Engagement leads who span circles. Cross-circle retrospectives. Documented handoff patterns. The integration of circle contributions is itself part of the engagement's value.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Each circle has documented playbooks, reference implementations, and quality bars ‖ The circle's craft is captured, not tribal; new joiners can ramp through artefacts; senior practitioners curate them as part of the role. | ☐ |
| 2 | Circle time is budgeted alongside billable time ‖ Sustained depth requires deliberate investment; the budget is visible and protected; practice work is evaluated as part of practitioner growth, not as side work. | ☐ |
| 3 | Mentorship and certification are stewarded within the circle ‖ Senior practitioners mentor juniors; circles maintain the firm's standing with platform vendors; certification levels are tracked and supported. | ☐ |
| 4 | Engagements requiring specialist depth pull from the relevant circle ‖ Generalist staffing for specialist work is recognised as the higher-cost option; the circle's expertise is brought from engagement start, not improvised when problems surface. | ☐ |
| 5 | COTS work is versioned, reviewed, and tested with the same discipline as code ‖ Power Platform flows, Salesforce configurations, Tableau models are engineering artefacts under governance, not tactical configurations no one owns. | ☐ |
| 6 | Legacy modernisation begins with knowledge extraction, not with technology selection ‖ The implicit logic of legacy systems is recovered, documented, and validated before rewrite; the strangler-fig pattern is the default; big-bang is the rare exception. | ☐ |
| 7 | Cross-circle engagement teams are formed deliberately ‖ Engagement leads span circles; staffing reflects the actual scope; the integration between circles' contributions is owned, not assumed. | ☐ |
| 8 | Inter-circle handoff patterns are documented and rehearsed ‖ How Platform integrates with Enterprise, how Legacy integrates with cloud-native, how COTS dashboards consume integrated data — these patterns are codified, not improvised per engagement. | ☐ |
| 9 | Vendor relationships and partner programmes are maintained by the circles ‖ Salesforce, Microsoft, Snowflake, Databricks partner standings are kept current; the firm's value to clients includes the depth of these vendor relationships. | ☐ |
| 10 | Cross-circle retrospectives drive learnings back to each circle's playbooks ‖ Engagements feed the practices that staffed them; learnings are not lost when an engagement closes; the circles compound experience over years. | ☐ |

---

## Related

[`technology/engagement-models`](../engagement-models) | [`technology/api-backend`](../api-backend) | [`technology/cloud`](../cloud) | [`technology/devops`](../devops) | [`principles/modernization`](../../principles/modernization) | [`principles/foundational`](../../principles/foundational)

---

## References

1. [Salesforce — Architect Resources](https://architect.salesforce.com/) — *salesforce.com*
2. [MuleSoft — Anypoint Platform](https://www.mulesoft.com/platform/api) — *mulesoft.com*
3. [Apache Kafka](https://kafka.apache.org/) — *kafka.apache.org*
4. [Microsoft Power Platform CoE Starter Kit](https://learn.microsoft.com/en-us/power-platform/guidance/coe/starter-kit) — *learn.microsoft.com*
5. [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/) — *learn.microsoft.com*
6. [Tableau](https://www.tableau.com/) — *tableau.com*
7. [Martin Fowler — Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html) — *martinfowler.com*
8. [Spotify Engineering — Scaling Agile](https://blog.crisp.se/wp-content/uploads/2012/11/SpotifyScaling.pdf) — *crisp.se*
9. [Etienne Wenger — Communities of Practice](https://www.wenger-trayner.com/introduction-to-communities-of-practice/) — *wenger-trayner.com*
10. [SEI CMMI Institute](https://cmmiinstitute.com/) — *cmmiinstitute.com*
