# HA & DR Systems

Architecture for systems that must keep running when components fail and recover when entire regions, datacentres, or providers do. High availability is the day-to-day discipline; disaster recovery is the once-a-year discipline; both require explicit design that production traffic never reveals until it is too late to add.

**Section:** `system-design/` | **Subsection:** `ha-dr/`
**Alignment:** Site Reliability Engineering | ISO 22301 | Chaos Engineering | AWS Well-Architected Reliability Pillar

---

## What "HA & DR" actually means

A *best-effort* approach to availability assumes most failures will be small, most recoveries will be automatic, and the rare large failure will be handled when it happens. The result is systems that handle minor incidents well and major incidents badly — because the patterns for minor handling (retry, restart, route around) are not the patterns for major handling (cross-region failover, data loss budgeting, coordinated recovery), and the team has only practised the small kind.

An *engineered availability* approach treats high availability and disaster recovery as different disciplines with different patterns. HA prevents downtime in normal operations: redundancy, health checks, automatic failover, load balancing, circuit breakers, bulkheads. DR recovers from disaster: backups with bounded recency, multi-region replication, runbooks for rebuilding, drill exercises that make the runbooks real. Both have measurable targets — recovery point objective (how much data can be lost) and recovery time objective (how long can recovery take) — that drive the architecture rather than describe it.

The architectural shift is not "we have backups." It is: **availability is engineered through specific patterns chosen against specific objectives, exercised regularly, and held to measurable bars — not assumed because the cloud provider has good marketing.**

---

## Six principles

### 1. HA and DR are different problems with different solutions

High availability prevents downtime during normal operations: a server fails, traffic routes elsewhere, the user never notices. Disaster recovery handles the rare scenarios HA cannot: a region goes dark, a provider has an extended outage, a cyber-attack destroys the primary database, a software bug corrupts production data across all replicas simultaneously. The patterns differ. HA optimises for fast detection and automatic remediation within a single environment. DR optimises for being able to rebuild in a different environment when the original is unrecoverable. Conflating them — calling the multi-region active-active deployment "DR" or treating the daily backup as "HA" — leaves both jobs incompletely done.

#### Architectural implications

- HA and DR strategies are designed separately, with separate runbooks, separate testing, and separate ownership where possible.
- Each system documents its HA targets (uptime SLO, mean time to recovery for component failures) and DR targets (RPO, RTO, what triggers a DR failover) as distinct commitments.
- Patterns chosen for HA (load balancers, health checks, automated failover within a region) are recognised as not solving the DR problem; patterns chosen for DR (cross-region replication, immutable backups, runbook-driven recovery) are recognised as not replacing HA.
- Tabletop and game-day exercises rehearse both kinds of failure separately, because rehearsing only the small kind leaves the team underprepared for the big kind.

#### Quick test

> Pick a critical service in your system. What is its strategy if a single instance crashes? What is its strategy if its primary region becomes unavailable for 24 hours? If those two strategies are the same, one of the two scenarios is not really being addressed.

#### Reference

[AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html) — the canonical separation of failure modes (component failure vs. zonal outage vs. regional disaster) and the patterns appropriate to each.

---

### 2. RPO and RTO are architectural constraints, not aspirations

Recovery Point Objective is the maximum acceptable data loss measured in time — "we can lose at most 5 minutes of writes." Recovery Time Objective is the maximum acceptable downtime — "we must be back online within 1 hour." These are not numbers the architect picks to feel good about; they are constraints the business owns, and they drive specific architectural decisions. RPO of zero requires synchronous replication across the recovery boundary. RPO of 5 minutes can use asynchronous replication with bounded lag. RTO of 1 hour can be met with manual failover and runbook-driven recovery. RTO of 1 minute requires automated failover, pre-warmed standby capacity, and tested DNS or routing changes. Stating these objectives explicitly forces the conversation about what they cost; leaving them implicit produces architectures that meet whatever objective is convenient and discover the gap during a real incident.

#### Architectural implications

- Each system has documented RPO and RTO, agreed with business stakeholders, with the cost of meeting them visible.
- The replication strategy (synchronous, asynchronous, snapshot-based) is chosen explicitly to meet the RPO, not as a default.
- The failover strategy (automatic, manual, runbook-driven, hybrid) is chosen explicitly to meet the RTO.
- The cost of the RPO/RTO commitment is part of the budget, not absorbed silently — meeting tight objectives is expensive in compute, network, and operational complexity.

#### Quick test

> Pick a system you operate. What is its documented RPO and RTO, and what was the actual data loss and recovery time the last time it had a serious incident? If the documented numbers and the actual numbers diverge by more than a factor of two, the architecture meets aspirations rather than constraints.

#### Reference

[ISO 22301 — Business Continuity Management](https://en.wikipedia.org/wiki/ISO_22301) — the international standard that defines RPO, RTO, and the broader business continuity discipline within which technical architectures sit.

---

### 3. Redundancy without failure detection is just expense

Two database replicas, both running, both up to date — a configuration that is supposed to be highly available. But if the failover requires noticing that the primary has failed, deciding which replica should take over, and switching traffic, and if any of those steps depends on a manual operator response in the middle of the night, the redundancy did not buy availability. It bought potential availability — actualised only when detection and switching work. Real HA requires that failure is detected automatically (within seconds, not minutes), that the decision logic for failover is correct (not split-brain, not flapping), and that the switch happens without human intervention. Without these, the second replica is paying full cost for partial benefit.

#### Architectural implications

- Health checks are continuous, exercise real functionality (not just "the process is running"), and have explicit thresholds that distinguish transient issues from genuine failure.
- Failover decisions are deterministic, idempotent, and avoid both split-brain (two replicas thinking they're primary) and flapping (rapid back-and-forth between replicas).
- The detection-to-recovery path is measurable end-to-end and tested under realistic failure injection.
- Manual escalation paths exist for cases where automation fails — but the automation handles the routine cases without waking anyone.

#### Quick test

> Pick a redundant system in your architecture. From the moment the primary fails, how long until the secondary takes over, and who or what makes that decision? If the answer involves a human looking at dashboards, the redundancy is providing recoverability rather than availability — a different (and much more expensive per nine) commitment.

#### Reference

[Site Reliability Engineering — How Google Runs Production Systems](https://sre.google/books/) — the canonical treatment of automated failure detection, the difference between "things are working" and "things are failing slowly," and why the gap between them is the entire engineering discipline.

---

### 4. Failover is dangerous; non-failover is dangerous; pick your danger

Automatic failover risks split-brain (both replicas accepting writes during a network partition), data loss (the new primary diverging from the old), and flapping (rapid failover-failback as conditions oscillate). Manual failover risks long downtime (waiting for a human to make the decision), human error under pressure (failing over the wrong way, missing a step), and decision paralysis (no one wants to be responsible for the call). There is no third option that is safe — every architecture picks which danger to accept and engineers around it. Designing as if failover is a clean operation produces systems that fail in surprising ways at the worst possible time, because the assumption was never tested under the conditions that matter.

#### Architectural implications

- The chosen failover model (automatic, manual, hybrid with thresholds) is documented along with the trade-offs it accepts.
- For automatic failover, the split-brain prevention mechanism (quorum, fencing, leader leases) is explicit and tested under network partitions.
- For manual failover, the runbook is written, current, and rehearsed — not a wiki page from two years ago that mentions services that no longer exist.
- The expected behaviour under partition (whether the system stops accepting writes, accepts writes with reduced consistency, or fails open) is documented and tested with real partition injection.

#### Quick test

> Pick a system with a documented failover mechanism. When was the last time it was exercised in production or production-equivalent conditions, with a real network partition or instance termination? If the answer is "we tested it once when we built it," the failover mechanism is now a fossil — present in the architecture but not known to work.

#### Reference

[Aphyr — Jepsen Analyses](https://jepsen.io/analyses) — the systematic, decade-long body of work demonstrating exactly how failover mechanisms in real distributed systems fail under partitions, and what can and cannot be safely guaranteed.

---

### 5. Disasters are rehearsed, not assumed

The DR runbook that has never been executed is, with very high probability, wrong. Steps are missing, references are stale, dependencies have changed since it was written, and the people who wrote it have left or forgotten. The first time the runbook is used at scale is the worst possible time to discover its gaps. The architectural commitment to availability includes the operational commitment to rehearsing the failure modes the architecture is supposed to handle — game days, chaos experiments, regional failover drills, full DR exercises. Without rehearsal, all the redundancy and replication and runbook-writing is theatre: it produces the appearance of availability without the property of availability.

#### Architectural implications

- Game days happen on a regular cadence (quarterly is common, monthly is better), include both technical and human responses, and produce findings that are tracked to closure.
- Chaos engineering experiments are part of normal operations, not a stunt — they verify that the system continues to meet its SLOs under controlled failure.
- Full DR drills exercise the actual recovery path (restore from backup, fail over to the alternate region, rebuild a service from scratch) at least annually, with the actual people who would do this in a real incident.
- Findings from drills are treated as P0 bugs in the availability architecture — not "interesting observations" — and resourced accordingly.

#### Quick test

> Pick the most recent DR drill in your organisation. Was it a real exercise (failing over real systems, restoring real backups, exercising real runbooks), or was it a tabletop discussion? If it was a tabletop, the drill exercised the conversation, not the architecture.

#### Reference

[Principles of Chaos Engineering](https://principlesofchaos.org/) — the formal articulation of the discipline, originating at Netflix, that makes failure injection a routine engineering practice rather than an extraordinary event.

---

### 6. Graceful degradation beats total failure

When part of the system fails, the choice is between three outcomes: the whole system fails, the affected part fails completely while the rest continues, or the affected part degrades gracefully (works in a reduced mode rather than failing entirely). The third is almost always better than the first two, but it requires deliberate design. Caching the last-known-good response when the upstream is unavailable. Returning a default rather than an error when a non-critical service is down. Disabling features rather than rejecting requests. Showing stale data with an indicator rather than no data at all. None of these happen by accident — they are engineering decisions that turn outages into inconveniences, and they accumulate into a system that stays useful through conditions that would have taken it down before.

#### Architectural implications

- Feature flags allow individual capabilities to be disabled without taking down the whole system.
- Circuit breakers prevent cascading failures by failing fast in known directions instead of slow and unpredictably.
- Caches with explicit staleness policies serve as fallbacks when upstreams are unavailable, with appropriate user-visible indicators of degraded quality.
- The user experience under various degradation modes is designed deliberately — including the messages users see when features are disabled or data is stale.

#### Quick test

> Pick a non-critical dependency in your system (a recommendation engine, a search service, a third-party API). What does the user experience look like when that dependency is unavailable? If the answer is "the page errors out" or "the request fails," the system has not been designed for graceful degradation — it has been designed for binary working/not-working states.

#### Reference

[Michael Nygard — Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/) — the canonical catalogue of stability patterns (circuit breaker, bulkhead, timeout, fail fast) that turn cascading failures into bounded ones, originating from production experience that predates modern observability tooling.

---

## Architecture Diagram

The diagram below shows a canonical HA & DR topology: a primary region with multi-AZ redundancy and automated failover within the region; a secondary region maintained for disaster recovery via asynchronous replication; health checks driving routing decisions; an immutable backup archive distinct from the replicated state; runbook-driven manual escalation for the rare cases automation cannot handle.

---

## Common pitfalls when adopting HA & DR thinking

### ⚠️ Backups without restore drills

Backups are taken nightly, stored carefully, and never verified by being restored. The first time the team actually restores from backup is during an incident, and that is when they discover the backups are corrupt, incomplete, or in a format the current system can no longer read.

#### What to do instead

Restore is part of the backup discipline. A backup that has not been restored recently is not known to be a backup — it is a hopeful set of files. Routine restore drills (to staging, to development, to a separate environment) verify the backup is what the team thinks it is.

---

### ⚠️ Multi-AZ as multi-region

Treating multi-availability-zone deployment as if it provided regional disaster recovery. AZs share a region; a regional outage takes down all AZs simultaneously; multi-AZ is HA, not DR. Teams that learned this distinction during a real regional outage learned it expensively.

#### What to do instead

Multi-AZ for HA, multi-region for DR. They are different patterns with different costs and different operational profiles. Conflating them produces architectures with neither property fully delivered.

---

### ⚠️ Untested runbooks

The DR runbook was written when the system was deployed three years ago. Services have been added, removed, renamed, restructured. The runbook references commands, hosts, and people that no longer exist. During an incident, the runbook becomes a confusing artifact rather than a guide.

#### What to do instead

Runbooks are living documents, exercised quarterly, updated whenever the system changes. The version that gets used in an incident is the same version that was rehearsed last quarter — not the version that has not been touched since the system launch.

---

### ⚠️ The single-point-of-failure that hides

The architecture claims redundancy at every layer, but there is one DNS provider, one TLS certificate authority, one CI/CD system, one secrets manager, one identity provider — any of which, if it fails, takes down the whole stack despite all the redundancy elsewhere. These single points hide because they are not part of "the application," but they are part of every customer interaction.

#### What to do instead

Trace the dependency graph for a customer interaction end-to-end. Every external service, every shared internal service, every infrastructure component is examined for redundancy. The hidden single points of failure are made visible, and the team decides explicitly whether to accept, hedge, or eliminate each one.

---

### ⚠️ Failure of imagination

Designing for the failure modes the team has experienced before, while remaining unprepared for the failure modes nobody on the team has lived through. The first regional outage the team encounters is the first time they truly think about regional outages — and that thinking happens during the outage, not before.

#### What to do instead

Read postmortems from other organisations, run pre-mortems on your own systems, do scenario exercises that include unfamiliar failure modes (complete provider outage, data corruption discovered three weeks late, malicious insider, prolonged regional unavailability). The exercises do not need to match every possible failure — they need to expand the team's imagination beyond what it has personally seen.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Each critical system has documented RPO and RTO agreed with business stakeholders ‖ Without numbers, every recovery decision is improvised. With numbers, the architecture either meets the commitment or visibly does not — and the gap becomes a budgeted item rather than a surprise during an incident. | ☐ |
| 2 | HA and DR strategies are documented separately, with separate testing ‖ They solve different problems with different patterns. Conflating them — calling multi-AZ deployment "DR" — leaves the team unprepared for the failure mode the conflation hid, which always turns out to be the one that happens. | ☐ |
| 3 | Health checks exercise real functionality, not just process liveness ‖ A process can be running and unable to serve requests. Health checks that verify the actual capability — that the database connection works, that downstream calls succeed, that the cache is reachable — are what makes detection trustworthy. | ☐ |
| 4 | Failover mechanisms are tested under realistic failure injection ‖ Failover that has never been triggered is a fossil — present in the architecture but not known to work. Routine injection (chaos experiments, controlled failovers) is what keeps the mechanism alive and verified. | ☐ |
| 5 | Game days run on a regular cadence with findings tracked to closure ‖ One game day per year produces theatre; quarterly game days produce muscle memory and a backlog of real architectural improvements. The findings are tracked like any other engineering work, not filed and forgotten. | ☐ |
| 6 | DR drills exercise actual recovery paths at least annually ‖ Tabletop discussions surface the gaps in mental models; real drills surface the gaps in the architecture. Both have value; neither replaces the other; the actual restore-from-backup-into-fresh-environment drill is irreplaceable. | ☐ |
| 7 | Backups are verified by routine restore, not just by completion of the backup job ‖ A backup that has never been restored is hopeful, not actual. Verification that restore produces a usable system in a realistic time window is part of the backup discipline, not a separate concern. | ☐ |
| 8 | Hidden single points of failure (DNS, CA, IdP, CI/CD) are mapped and explicitly accepted or hedged ‖ External dependencies tend to be single-vendor by default. The architecture either tolerates the failure of each one, has a workaround, or has accepted the risk in writing — not as an oversight discovered during the vendor's incident report. | ☐ |
| 9 | Graceful degradation modes exist for non-critical dependencies ‖ User experience under degradation is designed: caches serve stale data with indicators, non-critical features disable cleanly, errors are bounded rather than cascading. The system stays useful in conditions that would have taken it down without this discipline. | ☐ |
| 10 | Runbooks are living documents — exercised, updated when the system changes, current ‖ A runbook that has not been touched since deployment is a snapshot of an obsolete system, dressed up as a guide. The runbook that gets used in an incident is the same runbook that was rehearsed recently — or there is no useful runbook at all. | ☐ |

---

## Related

[`principles/cloud-native`](../../principles/cloud-native) | [`principles/foundational`](../../principles/foundational) | [`patterns/deployment`](../../patterns/deployment) | [`patterns/data`](../../patterns/data) | [`patterns/security`](../../patterns/security) | [`system-design/scalable`](../scalable)

---

## References

1. [AWS Well-Architected Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html) — *AWS*
2. [Google Site Reliability Engineering — Books](https://sre.google/books/) — *sre.google*
3. [Principles of Chaos Engineering](https://principlesofchaos.org/) — *principlesofchaos.org*
4. [ISO 22301 — Business Continuity Management](https://en.wikipedia.org/wiki/ISO_22301) — *Wikipedia*
5. [Aphyr — Jepsen Analyses](https://jepsen.io/analyses) — *jepsen.io*
6. [Michael Nygard — Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/) — *pragprog.com*
7. [Recovery Point Objective and Recovery Time Objective](https://en.wikipedia.org/wiki/Recovery_point_objective) — *Wikipedia*
8. [Disaster Recovery (Wikipedia)](https://en.wikipedia.org/wiki/Disaster_recovery) — *Wikipedia*
9. [High Availability (Wikipedia)](https://en.wikipedia.org/wiki/High_availability) — *Wikipedia*
10. [NIST SP 800-34 — Contingency Planning Guide](https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final) — *NIST*
