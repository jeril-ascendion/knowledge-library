# SLIs & SLOs

The discipline of converting reliability from a vague aspiration into a measured engineering target with a tradable budget — recognising that the SLI is a measurement, the SLO is a commitment, and the error budget is the architectural construct that connects the two to engineering decisions about velocity, risk, and prioritisation.

**Section:** `observability/` | **Subsection:** `sli-slo/`
**Alignment:** Google SRE Book | Google SRE Workbook (Burn Rate Alerts) | Service Level Objectives (Alex Hidalgo) | OpenSLO

---

## What "SLIs and SLOs" actually mean

Before SLIs and SLOs, *reliability* was either a vague aspiration ("we should be reliable") or a contract clause ("99.9% uptime in the SLA"). Neither produced engineering action: the aspiration was unmeasurable, and the SLA's penalty was small enough that it didn't drive day-to-day prioritisation. The architectural shift that the Google SRE community articulated and made canonical is to treat reliability as a measurable engineering target with three layered constructs.

A *Service Level Indicator (SLI)* is a measurement: the proportion of requests that are "good" — typically defined as serving correctly within a latency threshold — over a time window. The SLI is the *number*: 99.93% of requests in the last 28 days were good. A *Service Level Objective (SLO)* is a commitment: the institution declares that the SLI should be at least N% over the time window. The SLO is the *target*: we commit to 99.9% good over 28 days. An *error budget* is what the SLO leaves: if the SLO is 99.9%, the budget is 0.1% — and that 0.1% is a tradable resource. As long as the budget is intact, the team has license to take risks (deploy faster, run experiments, accept some ambient instability); when the budget is being consumed faster than it should be, the team's priority shifts to reliability work over feature work, by policy, until the budget is restored.

The architectural shift is not "we set a 99.9% target." It is: **reliability is an engineering construct with a measurable indicator (SLI), a documented commitment (SLO), and a tradable budget (error budget) that connects the system's actual reliability to engineering decisions — and treating reliability as anything less than this produces vague aspirations that don't drive action and SLAs that exist only on the day they're missed.**

---

## Six principles

### 1. The SLI is a measurement; the SLO is a commitment — confusing them obscures both

A common mistake: an organisation talks about its "SLO of 99.9% for the checkout service" without ever measuring the actual rate. The "SLO" is just a number on a slide, with no SLI behind it. Or: an organisation produces a dashboard showing "the SLI for the checkout service is 99.94% this month" with no documented commitment about what that should be. The SLI exists; the SLO doesn't. Both failure modes are real and both leave reliability outside engineering practice. The discipline is to maintain both as distinct, related, and visible: the SLI is computed continuously from telemetry, the SLO is documented and reviewed deliberately, and the relationship between the two — is the SLI meeting or missing the SLO, by how much, for how long — is the operational signal.

#### Architectural implications

- For each user-facing service, both an SLI definition (what's measured, over what window, with what threshold) and an SLO target (what value the SLI commits to) are documented.
- The SLI is computed continuously from production telemetry — not from synthetic tests, not from an aspirational dashboard, but from actual user request outcomes.
- The SLO is reviewed periodically (typically quarterly) against actual SLI performance — the SLO can be tightened (when consistently met with margin) or loosened (when consistently missed for reasons the team has accepted).
- The SLI and SLO together form the input to error-budget calculations and burn-rate alerting; without both, those downstream constructs have nothing to operate on.

#### Quick test

> Pick the most user-impactful service in your organisation. Is there a documented SLI definition, an SLO target, and a current measurement of the SLI over the SLO's time window? If any of the three is missing, the service has reliability-as-aspiration, not reliability-as-engineering — and the next time something degrades, the conversation about whether it's a problem will run on judgment rather than evidence.

#### Reference

[Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) is the foundational reference that introduced the SLI/SLO/SLA terminology and discipline; the chapter remains the canonical reference. [Service Level Objectives — Alex Hidalgo](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/) is the practitioner-level deep dive on SLO design and operation in production.

---

### 2. Choose SLIs by user experience, not by ease of measurement — the easy metrics often miss what users actually feel

A common pattern: the team chooses SLIs by what's easy to measure. CPU utilisation is easy; HTTP 5xx rate is easy; uptime measured by a simple ping is easy. None of these is the user experience. The CPU can be at 5% while users are seeing failures; the 5xx rate can be near zero while users are seeing slow degraded responses; the ping can be successful while the actual checkout flow is broken. The SLI's job is to measure user experience, which means thinking from the user's perspective: did the user's request succeed (correctly) and was it served in a reasonable time (latency under threshold)? The SLI is "proportion of valid user requests that were served correctly within latency threshold T over time window W." The metrics needed to compute this — request count by user-meaningful endpoint, error count by the user's definition of error, latency distribution at the response — may require more work to instrument than CPU utilisation, but the work pays for itself in SLIs that actually correlate with user-reported problems.

#### Architectural implications

- SLI definitions are user-experience-driven: "proportion of checkout requests that returned a successful response within 1 second" rather than "uptime" or "5xx rate."
- The SLI's "good" definition is documented explicitly — what counts as a successful response, what's the latency threshold, what user actions are in scope — and validated against user-reported problems.
- Where the easy-to-measure metric and the user-experience metric diverge (CPU is fine but users complain), the user-experience metric is treated as authoritative, and the easy metric is recognised as a poor proxy.
- SLIs are reviewed when user-reported problems aren't reflected in the SLI — the absence of correlation is a signal that the SLI isn't measuring what users feel.

#### Quick test

> Pick your most-trafficked SLI. Does it correlate with user-reported problems — when users complain, does the SLI show degradation, and when the SLI is healthy, are users happy? If the correlation is weak, the SLI is measuring something other than user experience — and it's a poor target for engineering work.

#### Reference

[Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/) treats user-experience-driven SLI choice as the central architectural discipline. [Service Level Objectives — Alex Hidalgo](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/) covers the practitioner-level design of SLIs that actually measure what users feel, with anti-patterns to avoid.

---

### 3. The error budget is an engineering construct that converts reliability into a tradable resource

The error budget is what makes the SLO operational. If the SLO is 99.9% over 28 days, the error budget is 0.1% × 28 × 24 × 60 = 40 minutes of unreliability allowed in the window. This budget is a *tradable resource*: as long as it's intact, the team has license to take risks (faster deploys, experiments, planned chaos engineering, accepting some ambient flakiness). When the budget is being consumed faster than it should be — regardless of cause: a rough deploy, a flaky dependency, an infrastructure incident — the team's priority shifts. Feature work decelerates; reliability work accelerates. The shift isn't a manager's call; it's a budget rule. The architectural payoff is that reliability becomes a quantified resource that connects directly to engineering decisions, and the perennial tension between "ship faster" and "be reliable" gets resolved by data rather than by argument.

#### Architectural implications

- The error budget is computed continuously: budget remaining = (1 - SLO) × time window − consumed unreliability so far.
- An *error budget policy* — a documented rule about what happens when the budget is consumed at certain rates — exists and is followed: e.g., "if more than 50% of the budget is consumed in the first half of the window, the team focuses on reliability work until the burn rate is acceptable."
- The policy is enforceable, not advisory — when the budget is exhausted, feature freezes happen, by policy, not by judgment.
- The budget's recovery is also tracked: as the unreliable window passes out of the rolling SLO window, the budget refills, and the team's license to take risks restores.

#### Quick test

> Pick your most consequential SLO. What's the current error budget, and what's the documented policy for when the budget reaches certain consumption levels? If the policy is "we'd think about it" rather than enforceable rules, the budget is a number, not a construct — and the next budget burn won't shift engineering priorities the way it should.

#### Reference

[Google SRE Book — Embracing Risk](https://sre.google/sre-book/embracing-risk/) introduces the error budget concept and its operational use. [Error Budget Policy (Google SRE)](https://sre.google/workbook/error-budget-policy/) covers the policy construct in practitioner detail, with templates and examples.

---

### 4. Alerting on burn rate, not on threshold — the rate of consumption matters, not the absolute level

A common pattern: alerts fire when the SLI dips below the SLO. "Latency exceeded 1s — page!" The problem: a brief dip below SLO threshold during normal traffic noise produces a noisy alert that's not actionable; a long, slow degradation that consumes most of the error budget without ever spiking below threshold doesn't fire at all. The right architectural construct is the *burn rate*: how fast is the error budget being consumed, normalised to the SLO window. A burn rate of 1 means consumption is matching the budget exactly (the budget will deplete exactly at end of window if the rate continues); a burn rate of 14.4 (used in Google SRE's standard alerts) means the budget is being consumed 14.4x faster than sustainable — alarming, actionable. Alerts on burn rate fire when the rate of consumption is too high, regardless of whether the absolute SLI is above or below the SLO threshold at any given moment, and that's the operationally meaningful signal.

#### Architectural implications

- Alerts on SLOs are constructed as burn-rate alerts, not threshold alerts: "fire when burn rate over [time window] exceeds [rate]."
- Burn rate is computed continuously from the SLI and SLO; the alert routing depends on the rate, not on the absolute SLI value at the moment.
- The choice of burn-rate threshold reflects a trade-off: a higher threshold (e.g. 14.4x) catches fast disasters with low false-positive rate; a lower threshold (e.g. 3x) catches slower burns but with more noise. Standard practice combines multiple thresholds (see next principle).
- Threshold-based alerts on raw SLI values are recognised as the wrong primitive for SLO management — they fire on noise, miss slow burns, and don't connect to the budget framework.

#### Quick test

> Pick the SLO alerts in your organisation. Are they burn-rate alerts or threshold alerts? If threshold alerts, the alerting is operating on instantaneous SLI values rather than budget consumption rate — and the next slow degradation that doesn't trip the threshold but consumes the budget will go unnoticed until it's late.

#### Reference

[Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) is the canonical reference for burn-rate alerting; it covers the math, the operational properties, and the trade-offs between different burn-rate thresholds. [Multi-Window Multi-Burn-Rate Alerts (Google SRE)](https://sre.google/workbook/alerting-on-slos/) specifically treats the multi-window pattern that's now industry-standard.

---

### 5. Multi-window multi-burn-rate alerts catch both fast disasters and slow burns

Even burn-rate alerts have a calibration problem: a single burn-rate threshold is either tuned for fast disasters (high threshold like 14.4x, short window like 1 hour — catches a service falling over but misses slow burns) or for slow burns (lower threshold like 3x, longer window like 6 hours — catches gradual degradations but is slow to fire on fast disasters and noisy on transient blips). The architectural answer is *multiple alerts at multiple windows and rates*, fired with appropriate routing: a *fast burn* alert (e.g. burn rate > 14.4x over 1 hour AND > 14.4x over 5 minutes) fires immediately for major incidents; a *slow burn* alert (e.g. burn rate > 3x over 6 hours AND > 3x over 30 minutes) fires for slower degradations that would consume significant budget if not addressed. The two-window construct prevents single-window noise (the secondary window must also trigger), and the multiple alerts cover the rate spectrum.

#### Architectural implications

- Each SLO has multiple burn-rate alerts at different rate-and-window combinations — typically a fast-burn alert and a slow-burn alert, sometimes a third for medium-rate burns.
- Each alert uses a primary window (the rate window) and a secondary window (a shorter check window to avoid firing on transient spikes that don't sustain).
- Alert routing differs by rate: fast-burn alerts page on-call immediately; slow-burn alerts may go to a ticket queue or business-hours channel; the routing matches the urgency.
- The multi-window approach is documented and the rate-window combinations are calibrated; defaults from the SRE Workbook are good starting points, but production-tuning requires observation.

#### Quick test

> Pick your most important SLO. How many burn-rate alerts does it have, and what's the rate and window for each? If there's only one alert, either fast disasters or slow burns are uncovered — and one of those failure modes will eventually surface in a way the alerting didn't catch.

#### Reference

[Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) is the canonical reference for multi-window multi-burn-rate alerts, with concrete formulas, recommended rate-window combinations (1-hour at 14.4x, 6-hour at 6x, etc.), and calibration guidance. The pattern has been adopted across the industry — [OpenSLO](https://openslo.com/) standardises the configuration format.

---

### 6. SLO calibration is iterative — too tight produces noise and feature freezes; too loose accepts user pain

The SLO target itself is a calibration. *Too tight* (e.g. setting 99.99% on a service that historically achieves 99.9%) produces consistent budget burn, near-permanent feature freeze under the error budget policy, and alert fatigue. The team learns to ignore the SLO; reliability becomes a number, not a discipline. *Too loose* (e.g. setting 99% on a service that easily achieves 99.9%) accepts more user pain than necessary; the budget is never consumed; the SLO doesn't drive any engineering decisions. Both failure modes leave reliability outside engineering practice. The discipline is to set the SLO at a level where it's *occasionally challenging* — the budget is mostly intact but consumed sometimes, the alerting fires on real degradations not on noise, the policy is invoked occasionally, and the engineering investment that the policy demands actually produces reliability improvements that show up in the SLI. The calibration is iterative: SLOs are revisited (typically quarterly) and adjusted based on actual performance, user-experience evidence, and the policy's operational signal.

#### Architectural implications

- SLOs are reviewed on a documented cadence (typically quarterly) against actual SLI performance, user-reported problems, and policy invocation history.
- Persistently-met SLOs (no budget consumption, no alerts firing) are candidates for tightening — they're not driving engineering work.
- Persistently-missed SLOs (constant budget burn, near-permanent feature freeze) are candidates for either loosening (if the missed level is acceptable user experience) or for major investment (if the missed level is unacceptable and the system needs reliability work).
- The SLO is a designed property, not a decreed one — its calibration reflects operational reality and gets updated as the system evolves.

#### Quick test

> Pick your most important SLO. Over the last quarter, how often was the error budget significantly consumed (> 50% of budget burned in less than half the window), and how often did alerts fire? If the answer is "almost always" or "almost never," the SLO is mis-calibrated — too tight in the first case, too loose in the second — and is producing the failure mode that calibration is supposed to prevent.

#### Reference

[Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/) treats SLO calibration explicitly, with the iterative discipline of starting with a reasonable target and adjusting based on observation. [Service Level Objectives — Alex Hidalgo](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/) covers calibration patterns and anti-patterns at practitioner depth, including the "aspirational SLO" anti-pattern (set high, never met, ignored).

---

## Architecture Diagram

The diagram below shows the canonical SLI/SLO architecture: telemetry feeding SLI computation; SLO target as documented commitment; error-budget calculation and tracking; multi-window multi-burn-rate alerts on the budget consumption rate; the error budget policy as a rule that connects budget state to engineering decisions; calibration loop reviewing SLO targets quarterly against observed performance.

---

## Common pitfalls when adopting SLI/SLO thinking

### ⚠️ SLO without SLI — or vice versa

The team has a "99.9% target" with no continuous measurement, or a continuous measurement with no documented commitment. Reliability lives as either aspiration (no measurement) or curiosity (no commitment). Engineering decisions don't follow from either.

#### What to do instead

Both as distinct, related, and visible: SLI is computed continuously from telemetry, SLO is documented and reviewed deliberately, and the relationship between the two drives operational signals and engineering decisions.

---

### ⚠️ SLI by ease of measurement

The team picks CPU utilisation or 5xx rate as the SLI because it's easy. Users complain about slow checkouts; the SLI says everything is fine because checkout slowness doesn't show up as 5xx errors. The SLI doesn't correlate with user experience.

#### What to do instead

SLI defined by user experience: proportion of valid user requests served correctly within latency threshold. Validated against user-reported problems. The harder-to-instrument metric is the right one when the easy metric doesn't reflect what users feel.

---

### ⚠️ Error budget as decoration

The team computes an error budget but doesn't have a policy for what happens when it's consumed. The number sits on a dashboard. Budget burn doesn't shift engineering priorities. The construct is theatre.

#### What to do instead

A documented, enforceable error budget policy. When the budget reaches consumption thresholds, feature work decelerates and reliability work accelerates by rule, not by argument.

---

### ⚠️ Threshold alerts on SLOs

Alerts fire when the SLI dips below the SLO at any moment. Brief noise during normal traffic produces alert fatigue. Slow burns that consume most of the budget without spiking go unnoticed.

#### What to do instead

Burn-rate alerts: fire when the budget consumption rate over a time window exceeds a threshold. Multi-window multi-burn-rate combinations cover both fast disasters and slow burns.

---

### ⚠️ Set-and-forget SLO

The SLO was set three years ago and never reviewed. The system has changed, traffic has changed, the SLI has been at 99.99% for a year (SLO was 99.9%). The SLO drives no engineering decisions.

#### What to do instead

SLOs reviewed quarterly against actual performance. Persistently-met SLOs are candidates for tightening; persistently-missed SLOs are candidates for loosening or major investment. The calibration is ongoing.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Each user-facing service has both a documented SLI definition and a documented SLO target ‖ Both as distinct, related, and visible. SLI is the measurement; SLO is the commitment; the relationship drives operational signals. | ☐ |
| 2 | The SLI is defined by user experience — proportion of valid requests served correctly within latency threshold ‖ Not CPU utilisation, not 5xx rate, not uptime. The harder-to-instrument metric is the right one when easier metrics don't reflect what users feel. | ☐ |
| 3 | The SLI is computed continuously from production telemetry, not synthetic tests ‖ Real user request outcomes, not aspirational dashboards. The SLI tracks actual user experience, not the experience the team hopes users are having. | ☐ |
| 4 | The error budget is computed continuously and visible to the team ‖ Budget remaining = (1 − SLO) × window − consumed unreliability. The number is operational, not decorative. | ☐ |
| 5 | An error budget policy is documented and enforceable ‖ When the budget reaches consumption thresholds, engineering priorities shift by rule. Feature freezes happen by policy, not by judgment. | ☐ |
| 6 | Alerts on SLOs are burn-rate alerts, not threshold alerts ‖ Fire on the rate of budget consumption over a time window, not on instantaneous SLI value. The burn rate is the operationally meaningful signal. | ☐ |
| 7 | Multi-window multi-burn-rate alerts cover both fast disasters and slow burns ‖ A fast-burn alert (high rate, short window) catches major incidents immediately; a slow-burn alert (lower rate, longer window) catches gradual degradation. The combination covers the rate spectrum. | ☐ |
| 8 | Each alert uses a primary and secondary window to prevent firing on transient spikes ‖ Alert fires only when both the rate window and a shorter check window exceed thresholds. Reduces noise without missing real burns. | ☐ |
| 9 | SLOs are reviewed on a documented cadence against actual SLI performance and user-experience evidence ‖ Calibration is iterative. Quarterly review for tightening (persistently-met) or loosening / major investment (persistently-missed). | ☐ |
| 10 | The SLO/SLI/error-budget framework is the input to engineering prioritisation, not just a dashboard ‖ Reliability becomes a quantified engineering construct that connects to feature-vs-reliability prioritisation by data. The construct drives action; it doesn't merely report state. | ☐ |

---

## Related

[`observability/incident-response`](../incident-response) | [`observability/metrics`](../metrics) | [`observability/logs`](../logs) | [`observability/traces`](../traces) | [`technology/devops`](../../technology/devops) | [`patterns/structural`](../../patterns/structural)

---

## References

1. [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — *sre.google*
2. [Google SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/) — *sre.google*
3. [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) — *sre.google*
4. [Service Level Objectives — Alex Hidalgo](https://www.oreilly.com/library/view/implementing-service-level/9781492076803/) — *oreilly.com*
5. [OpenSLO](https://openslo.com/) — *openslo.com*
6. [Error Budget Policy (Google SRE)](https://sre.google/workbook/error-budget-policy/) — *sre.google*
7. [Google SRE Book — Embracing Risk](https://sre.google/sre-book/embracing-risk/) — *sre.google*
8. [Multi-Window Multi-Burn-Rate Alerts](https://sre.google/workbook/alerting-on-slos/) — *sre.google*
9. [The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/) — *sre.google*
10. [Distributed Systems Observability (Cindy Sridharan)](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/) — *oreilly.com*
