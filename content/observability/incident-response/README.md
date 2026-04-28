# Incident Response

The operational discipline that turns service degradation into resolved problem — recognising that detection, severity-routing, response coordination, communication, and learning are distinct activities that succeed or fail independently, and that the architecture supporting each is what determines whether incidents resolve in minutes or hours.

**Section:** `observability/` | **Subsection:** `incident-response/`
**Alignment:** Google SRE Book | Etsy — How to Conduct a Postmortem | PagerDuty Incident Response | ITIL Incident Management

---

## What "incident response" actually means

A *primitive* incident response process looks like this: a user complains, an engineer notices, the engineer pages a colleague, they investigate, eventually find the problem, fix it, and move on — possibly writing a brief note about what happened. The activity is reactive, dependent on individual heroics, and produces no institutional learning. Each incident teaches the responders, but the institution is no smarter for it; the next similar incident plays out the same way.

A *mature* incident response architecture treats the same situation as a structured operational discipline with distinct phases that can be designed, measured, and improved independently. *Detection* is a system property — automated alerts firing on the right signals at the right thresholds, with a documented mean time to detect (MTTD) that's tracked over time. *Severity classification* is a routing primitive — a sev1 (full outage, customer-impacting) gets one response (page the on-call, declare an incident, commander appointed); a sev3 (degradation in non-critical path) gets a different one (ticket queued, addressed in business hours). *Response coordination* uses defined roles — incident commander, communications lead, scribe — drawn from frameworks like the Incident Command System used in emergency response. *Communication* runs on documented channels — internal status, customer-facing status page, executive briefings — each with templates and cadences. *Post-incident review* is blameless and structured, producing actions tracked through completion. The discipline is not to *prevent* incidents (impossible) but to *resolve them faster, learn from them more, and prevent the next class of similar ones from occurring*.

The architectural shift is not "we wrote some runbooks." It is: **incident response is a multi-phase operational discipline whose architectural support — detection signals, severity routing, role structures, communication channels, learning loops — determines whether the organisation gets faster and smarter over time, or accumulates incidents the way it accumulates technical debt.**

---

## Six principles

### 1. Detection and response are separate disciplines — designing them as one obscures both failures

A common pattern conflates detection (the system noticing something's wrong) with response (the team doing something about it). The conflation produces architectures where alert thresholds are set so that humans can respond — meaning thresholds are loose to avoid alert fatigue, meaning real problems aren't detected until they're severe. Conversely, separating the two lets each be optimised for its own goal: detection optimised for *catching real problems early* (which means tighter thresholds, more signals, lower noise); response optimised for *producing fast, calm, effective resolution* (which means automation where possible, clear roles where automation can't, and consolidated alerts that group related signals into single incidents). The architectural discipline is to design detection for sensitivity and response for effectiveness, with a routing layer between them that escalates only what response actually needs.

#### Architectural implications

- Detection signals are tuned for catching real problems, not for tolerable alert volume — alert fatigue is solved at the routing layer (consolidation, intelligent grouping, severity routing) rather than by making detection less sensitive.
- A clear distinction exists between "alert fired" (detection event) and "incident declared" (response triggered) — not every alert escalates to an incident; an alerting layer with deduplication and correlation sits between detection and response.
- Response architecture is optimised for fast, calm resolution: documented roles, escalation paths, automation for routine recovery actions, runbooks for non-routine ones, and clear declaration of when an incident starts and ends.
- Mean time to detect (MTTD) and mean time to resolve (MTTR) are tracked separately and trended over time; improving each requires different actions.

#### Quick test

> Pick a recent incident in your organisation. How many minutes elapsed between the underlying problem starting and detection firing (MTTD)? Between detection and the responders engaging (response latency)? Between engagement and resolution (MTTR)? If those are bundled into a single number ("the incident lasted 47 minutes"), the discipline is unable to improve any phase independently — and the bottleneck phase, whichever it is, stays the bottleneck.

#### Reference

[Google SRE Book — Chapter 12: Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) treats detection and response as architecturally separable concerns; the framework distinguishes monitoring (the detection system) from incident response (the operational discipline) and treats their interfaces (alerting, severity routing) as designed properties rather than emergent ones.

---

### 2. Severity classification is a routing primitive — different severities deserve categorically different responses

A small organisation can treat all incidents the same: page everyone, all-hands, fix it. A large organisation cannot — the cost of all-hands response to every minor degradation is unsustainable, and the cost of soft response to a critical outage is worse. Severity classification is the routing primitive that solves this: a documented taxonomy (sev1 through sev5, or critical/high/medium/low) with clear criteria, applied at incident declaration, that determines which response pattern triggers. *Sev1* (e.g. full outage, payment system down, data loss in progress) gets immediate page, incident commander appointed, customer-facing status published, executive notified. *Sev2* (significant degradation, partial outage, customer-impacting performance) gets paged response within an SLA, internal coordination, customer comms if user-visible. *Sev3* (degradation in redundant or non-critical path) gets ticketed for business-hours work. The architectural discipline is to make these criteria explicit, train people to apply them, and trust the classification rather than treating every incident as severity-0 or severity-N depending on who's awake.

#### Architectural implications

- Severity criteria are documented with concrete examples — not just "high impact" but "user-facing service unavailable, OR data loss, OR loss of regulated logging."
- The classification produces routing: each severity has a documented response pattern (who pages, what cadence of updates, who is communications lead, what status surfaces are activated).
- Severity can be revised mid-incident as scope becomes clear — a sev2 that turns out to be a database corruption escalates; a sev1 that turns out to be a misclassified deploy de-escalates — and the routing adjusts.
- Severity is tracked as a metric: counts per severity per period, MTTD/MTTR per severity, escalations from one severity to another, providing operational insight into the system's incident profile.

#### Quick test

> Pick the most recent incident. Was its severity classified at declaration? Was the response pattern documented for that severity? Was the severity revisited as the incident developed? If severity classification was implicit ("it felt important"), the response was running on individual judgment rather than designed routing — and the cost is paid in mismatched response across different incidents and different responders.

#### Reference

[PagerDuty Incident Response Documentation](https://response.pagerduty.com/) provides an industry-canonical severity taxonomy (sev1–sev5) with concrete criteria and response patterns, freely available for adaptation. [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook) covers similar ground with different severity vocabulary, useful for organisations that prefer the high/medium/low framing.

---

### 3. Coordination roles — commander, scribe, communications lead — make the response work as a system

In a major incident, multiple engineers are simultaneously investigating, multiple stakeholders are asking for updates, and the team is operating under time pressure. Without defined roles, the response becomes chaos: investigators interrupt each other with questions, status updates get duplicated, customer comms either don't happen or happen contradictorily across surfaces, and the team's effective bandwidth is much lower than the sum of its individuals. The Incident Command System (ICS), originally developed for emergency response and adopted by software organisations, defines roles that make coordinated response possible: *Incident Commander* (decides priorities, makes calls when there's disagreement, owns the response — but does not investigate); *Operations Lead* (drives the technical investigation and remediation work); *Communications Lead* (handles all internal and external updates, freeing investigators); *Scribe* (maintains the incident timeline, records decisions and actions). For smaller incidents, one person plays multiple roles; for larger ones, the roles separate. The architectural discipline is to have the role structure defined and trained on, so that when a sev1 hits at 3 AM, people fall into their roles automatically rather than colliding.

#### Architectural implications

- Roles are documented with explicit responsibilities and explicit non-responsibilities (the Incident Commander does not investigate; the investigators do not communicate to customers).
- Role assignment is part of the incident declaration ritual — within minutes of declaration, the roles are filled, and everyone knows who's playing each.
- Tooling supports the structure: the chat channel for the incident has the roles displayed, the status page tooling routes through the Communications Lead, the timeline tool routes through the Scribe.
- People are trained on the roles, including how to step into them under pressure and how to hand off as roles fatigue (a Commander on a 6-hour incident hands off to a fresh Commander; the role doesn't end when the original person tires).

#### Quick test

> Pick a recent multi-hour incident in your organisation. Who was the Incident Commander, who was Communications Lead, who was Scribe? If those questions don't have clean answers, the response was running without role structure — and the cost was paid in duplicated work, mixed messages, and an incident timeline that has to be reconstructed afterwards from chat scrollback.

#### Reference

[Incident Command System (ICS) — FEMA](https://training.fema.gov/is/courseoverview.aspx?code=IS-100.c) is the canonical original reference for the role structure, developed for emergency-services coordination; the structure has been adapted to software incident response by [PagerDuty](https://response.pagerduty.com/), [Google SRE](https://sre.google/sre-book/managing-incidents/), and others, with the role names and responsibilities consistent across adaptations.

---

### 4. Runbooks live on a spectrum from prose to automation — choose the placement deliberately per recovery action

A *runbook* — documented steps to take in response to a specific signal or scenario — exists somewhere on a spectrum from pure prose ("if you see this alert, check X, then Y, then Z") to full automation ("when this alert fires, execute this script that performs the recovery"). The right placement depends on the recovery action's properties. Actions that are *frequently performed*, *deterministic*, and *low-risk* belong on the automation end — the system performs them without human intervention, surfacing only the result. Actions that are *infrequent*, *judgment-requiring*, or *high-risk* (irreversible changes, financial actions, security-sensitive operations) belong on the prose end — humans execute with guidance, but the decision and the responsibility remain human. The architectural mistake is uniform treatment: automating everything (including high-stakes actions that should require human judgment) or scripting nothing (forcing humans through routine recovery work that machines could handle). Each runbook gets a deliberate placement.

#### Architectural implications

- Each runbook (or each action within a runbook) is classified on the prose-to-automation spectrum, with the placement justified.
- Frequently-performed deterministic actions (restart this service, drain this node, scale this group) are automated, with the automation tested in non-production and exercised in game days.
- Infrequent or judgment-requiring actions are written as prose runbooks with sufficient context for a fresh responder to execute correctly under pressure — the runbook teaches as it directs.
- The runbook collection is a living document: actions that consistently get bypassed because the runbook is wrong get fixed; actions that are now automated have their prose runbooks updated to reflect the automated path.

#### Quick test

> Pick a routine recovery action in your organisation — restarting a service after a known failure mode, draining a misbehaving node, rotating a credential. Is it automated, runbook-prose, or "everyone just knows"? If it's "everyone just knows," the action depends on tribal knowledge, and the next responder who doesn't have it will execute differently. If it's runbook-prose for an action that's frequent and deterministic, human time is being spent where automation could free it.

#### Reference

[Google SRE Workbook — Runbook Anti-Patterns](https://sre.google/workbook/) covers the spectrum from automation to prose, with treatment of when to automate and when not. [Atul Gawande, *The Checklist Manifesto*](https://atulgawande.com/book/the-checklist-manifesto/) treats the design of prose checklists in high-stakes domains, with principles that transfer to incident-response runbook design.

---

### 5. Post-incident review is blameless or it doesn't work — and the alternative is repeated incidents

A post-incident review (post-mortem) is the discipline by which the institution learns from an incident: what happened, why, what would have caught it earlier, what changes should be made. The review's value depends entirely on its honesty. *Blameful* reviews — focused on identifying the individual who made the mistake — produce defensive responses, shallow findings, and a culture where engineers hide problems rather than surface them. *Blameless* reviews — focused on the system that allowed the incident to happen — produce honest accounts, deeper findings, and a culture where engineers proactively raise risks because they know doing so won't produce blame. The architectural construct here is the *facilitation framework*: the review is run by someone with explicit authority to keep it blameless, the structure separates "what happened" (timeline, factual) from "why it happened" (system analysis) from "what we'll change" (actions), and the actions are tracked through completion. Without the facilitation, "blameless" is a label the team applies to reviews that aren't actually blameless.

#### Architectural implications

- Post-incident reviews are scheduled within a documented window (typically 1–2 weeks) and run with explicit blameless framing — not "who made the mistake" but "what conditions made this kind of mistake possible."
- The review's structure separates timeline (factual reconstruction), analysis (contributing factors at the system level), and action items (concrete changes with owners and target dates).
- Action items are tracked through completion in the same systems used for engineering work, with periodic review of overdue items — a review that produces actions that don't ship is theatre.
- The reviews are made available across the organisation (with appropriate redactions for sensitive content) — institutional learning depends on more than the people in the room hearing the lesson.

#### Quick test

> Pick a major incident from 6+ months ago in your organisation. Was a post-mortem written? Were action items produced? Have they shipped? If the answers are "yes, yes, partially," the discipline is working. If the answers are "yes, yes, we don't track that," the post-mortem is producing artefacts that aren't producing change — and similar incidents will continue.

#### Reference

[Etsy — How to Conduct a Postmortem (Allspaw)](https://www.etsy.com/codeascraft/blameless-postmortems) — the seminal practitioner-level reference for blameless post-mortem culture, including specific framing techniques to keep the review honest. [Distributed Systems Observability — Cindy Sridharan](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) covers the post-mortem-as-architectural-feedback discipline in depth.

---

### 6. Time-to-detect, time-to-resolve, and incident frequency are engineering metrics — measured, trended, acted on

The incident-response system's own performance is measurable, and the metrics tell a different story than incident-narrative summaries do. *Mean Time To Detect* (MTTD) — from problem starting to detection firing — surfaces the detection layer's effectiveness independent of response. *Mean Time To Resolve* (MTTR) — from detection to resolution — surfaces the response layer's effectiveness. *Incident frequency* by severity — how often sev1, sev2, etc. fire per period — surfaces the system's overall reliability profile. *Incident-class repetition* — how often a similar root cause produces a new incident — surfaces whether learning is actually preventing recurrences. These metrics are tracked, trended, and acted on the same way other engineering metrics are: a deteriorating MTTD signals that detection coverage isn't keeping up with the system's evolution; a deteriorating MTTR signals that response architecture (runbooks, role training, tooling) needs investment; rising incident frequency in a category signals that engineering remediation isn't shipping the changes the post-mortems called for.

#### Architectural implications

- MTTD and MTTR are measured per incident and aggregated by severity, period, and service area; trends are monitored as actively as availability or latency.
- Incident frequency is tracked by category (data plane vs control plane, service A vs service B, deploy-related vs ambient) — aggregate counts hide patterns that specific categories surface.
- Repeat-class incidents are flagged: an incident whose root cause matches a prior incident is a strong signal that the prior post-mortem's actions didn't ship or didn't address the right cause.
- The metrics drive investment: MTTD problems route to detection-and-alerting work; MTTR problems route to runbook, automation, and training work; frequency problems route to engineering remediation of recurring root causes.

#### Quick test

> Pick the last quarter. What was the MTTD across sev1 and sev2 incidents, MTTR across the same, and incident frequency by severity? What's the trend? If those numbers don't exist, the incident-response system is running without engineering signal — and improvement is whatever happens by accident rather than by design.

#### Reference

[Google SRE Book — Practical Alerting and Service-Level Objectives](https://sre.google/sre-book/practical-alerting/) treats MTTD and MTTR as primary engineering metrics; the same chapter introduces error budgets that connect incident frequency to engineering investment. [DORA Metrics](https://dora.dev/) treats MTTR as one of the four key engineering performance metrics, alongside deployment frequency, lead time, and change failure rate.

---

## Architecture Diagram

The diagram below shows the canonical incident-response architecture: detection signals flowing into an alerting layer with deduplication and correlation; severity classification routing to differentiated response patterns; coordination roles (commander, communications, scribe) instantiated on declaration; runbook/automation execution path with documented escalation; post-incident review with blameless framing producing action items tracked through completion; metrics layer (MTTD, MTTR, frequency, repetition) feeding back into engineering investment.

---

## Common pitfalls when adopting incident-response thinking

### ⚠️ Detection tuned for human bandwidth

Alert thresholds are set loose so the team can keep up with the volume. Real problems hide below threshold. By the time something escalates loudly enough to alert, the impact is severe.

#### What to do instead

Detection tuned for catching real problems early. Alert volume managed at the routing/consolidation layer (deduplication, intelligent grouping, severity-based routing), not by making detection less sensitive.

---

### ⚠️ Severity by gut feel

Every incident is whatever severity the responder assigns based on how the situation feels. Some sev1s are over-classified; some sev3s are under-classified. Response patterns are inconsistent.

#### What to do instead

Documented severity criteria with concrete examples. Severity assigned at declaration, revisited mid-incident as scope clarifies. Severity routing produces consistent response per class.

---

### ⚠️ The Incident Commander who's also investigating

The most senior engineer is on the page; they take over coordination AND lead the technical investigation. Coordination decisions get delayed (they're heads-down debugging); investigation gets interrupted (they're answering status requests). Both suffer.

#### What to do instead

Roles are separate. The Incident Commander coordinates, doesn't investigate. The Operations Lead investigates, doesn't communicate. The Communications Lead handles updates. For small incidents, one person plays multiple roles deliberately; for large ones, the roles separate.

---

### ⚠️ Blameless in name, blameful in practice

The team labels post-mortems "blameless" but the conversation focuses on the engineer who pushed the deploy that caused the incident. The label is a slogan; the culture is the practice. Engineers learn that surfacing risks produces consequences and stop doing it.

#### What to do instead

Active facilitation by someone with authority to keep the framing honest. Structure separates "what happened" (timeline) from "why it happened" (system) from "what we'll change" (actions). The discipline is enforced, not assumed.

---

### ⚠️ Action items that don't ship

Post-mortems produce action items. The action items live in a spreadsheet. Six months later, the same incident class recurs because the action items never made it into engineering plans.

#### What to do instead

Action items live in the same engineering tracking system as feature work, with owners and target dates. Periodic review of overdue items. Repeat-class incidents trigger investigation of why prior actions didn't ship.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Detection is tuned for catching real problems early; alert volume managed at routing layer ‖ Detection sensitivity isn't compromised by alert fatigue. The routing layer (consolidation, deduplication, severity-based routing) handles volume, not the threshold tuning. | ☐ |
| 2 | Severity criteria are documented with concrete examples; severity is assigned at declaration ‖ Severity is a routing primitive, not a label. Concrete criteria mean different responders classify the same situation similarly. Severity is revisited mid-incident as scope clarifies. | ☐ |
| 3 | Each severity has a documented response pattern — paging cadence, comms surfaces, role activation ‖ Different severities deserve categorically different responses. The pattern per severity is documented; the routing produces consistent response. | ☐ |
| 4 | Coordination roles (Commander, Operations, Communications, Scribe) are documented and trained on ‖ ICS-derived roles, with explicit responsibilities and explicit non-responsibilities. Role assignment is part of the incident declaration ritual. People can step into roles under pressure. | ☐ |
| 5 | Runbooks are placed deliberately on the prose-to-automation spectrum per action's properties ‖ Frequent deterministic low-risk actions are automated. Infrequent judgment-requiring actions are prose-runbook. The placement is justified, not uniform. | ☐ |
| 6 | Automation is tested in non-production and exercised in game days ‖ Automation that hasn't been tested fails on the first incident. Game days exercise both the automation and the human response patterns, surfacing gaps before incidents do. | ☐ |
| 7 | Post-incident reviews are blameless with active facilitation ‖ Blameless is a practice, not a label. Facilitation by someone with authority to keep the framing honest. Structure separates timeline, analysis, actions. | ☐ |
| 8 | Action items are tracked in engineering systems with owners and target dates; overdue items are reviewed ‖ Actions live in the same tracking system as feature work. Repeat-class incidents trigger investigation of why prior actions didn't ship. The post-mortem produces change, not artefacts. | ☐ |
| 9 | MTTD, MTTR, incident frequency by severity, and repeat-class rate are tracked and trended ‖ The incident-response system's own performance is measured. Different metrics signal different work: MTTD problems → detection investment; MTTR problems → response investment; frequency problems → engineering remediation. | ☐ |
| 10 | Reviews are made available across the organisation with appropriate redactions ‖ Institutional learning depends on more than the people in the room hearing the lesson. Cross-team availability spreads the lesson; appropriate redactions handle sensitive content without losing the learning. | ☐ |

---

## Related

[`observability/sli-slo`](../sli-slo) | [`observability/metrics`](../metrics) | [`observability/logs`](../logs) | [`observability/traces`](../traces) | [`runbooks`](../../runbooks) | [`technology/devops`](../../technology/devops)

---

## References

1. [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — *sre.google*
2. [Etsy — How to Conduct a Postmortem](https://www.etsy.com/codeascraft/blameless-postmortems) — *etsy.com*
3. [PagerDuty Incident Response](https://response.pagerduty.com/) — *response.pagerduty.com*
4. [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook) — *atlassian.com*
5. [Incident Command System (ICS) — FEMA](https://training.fema.gov/is/courseoverview.aspx?code=IS-100.c) — *fema.gov*
6. [Google SRE Workbook](https://sre.google/workbook/table-of-contents/) — *sre.google*
7. [DORA Metrics](https://dora.dev/) — *dora.dev*
8. [Distributed Systems Observability (Cindy Sridharan)](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) — *oreilly.com*
9. [The Checklist Manifesto — Atul Gawande](https://atulgawande.com/book/the-checklist-manifesto/) — *atulgawande.com*
10. [ITIL Incident Management](https://www.axelos.com/certifications/propath/itil-4) — *axelos.com*
