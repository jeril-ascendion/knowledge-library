# Cloud

**Cloud-Native Blueprints — architecting for high availability, resilience, and 12-factor scalability.** Cloud is no longer a deployment target; it is the architecture itself. This page describes how we approach the major hyperscalers (AWS, Azure, Google Cloud), the patterns of cloud-native architecture, and the discipline of running cloud workloads cost-effectively and securely at scale.

**Section:** `technology/` | **Subsection:** `cloud/`
**Alignment:** AWS Well-Architected | Azure Well-Architected Framework | GCP Architecture Framework | Twelve-Factor App

---

## What "cloud" actually means

Cloud is three architectural commitments at once. It is a *purchasing model* — pay-as-you-go, elastic, no upfront capex. It is a *deployment model* — managed services that replace what teams used to operate themselves. It is a *design model* — patterns (statelessness, environment configuration, externalised state) that make applications portable, resilient, and operationally tractable at scale.

Treating cloud as just the first — moving servers from a data centre to AWS without changing the architecture — gives the worst of both worlds: cloud bills with on-prem operational profile, no elasticity, no resilience, no benefit. The patterns in this page assume the second and third are also adopted, deliberately, because that's where the actual value of the cloud lives.

---

## Six principles

### 1. Cloud choice is shaped by team, geography, and existing tooling

AWS, Azure, and GCP each have technical strengths (AWS's breadth, Azure's enterprise integration, GCP's data and ML platforms) and organisational consequences (the talent market, the existing licensing relationship, the team's familiarity, the regulatory profile of available regions). Picking on a feature comparison alone — "GCP has BigQuery, we want BigQuery" — produces architectures that fit the chosen platform but not the team that has to operate them. The right cloud is the one where technical fit and organisational fit converge.

#### Architectural implications

- The choice considers existing licensing relationships (Microsoft enterprise agreements often tilt to Azure; Google Workspace shops often tilt to GCP).
- Talent depth in the geography is real — recruiting senior AWS engineers in some markets is dramatically easier than recruiting senior GCP engineers, or vice versa.
- Regulatory geography matters: data residency, sovereign clouds (Azure Germany, GCP regions in regulated jurisdictions), and certifications (FedRAMP, IRAP, MTCS) constrain the choice in regulated industries.
- Multi-cloud is a separate decision (see principle 2) — the primary cloud is one decision, with documented trade-offs, made deliberately.

#### Reference

[Gartner — Magic Quadrant for Cloud Infrastructure and Platform Services](https://www.gartner.com/) — the canonical industry comparison covering capability breadth, vision, and the operational considerations beyond feature lists.

---

### 2. Multi-cloud is a strategy, not a default

The instinct to "go multi-cloud for resilience" sounds prudent and is usually wrong. Operating across two hyperscalers means the team has to manage two IAM systems, two networking models, two billing structures, two tooling stacks, two on-call rotations — every operational complexity is roughly doubled. The benefits are narrow: a hedge against vendor lock-in (rarely realised), genuine regulatory or data-residency requirements, and rare cases of best-of-breed service consumption. Most teams that adopt multi-cloud do so without these specific reasons and pay the operational tax forever. Multi-cloud is a strategy chosen for reasons; single-cloud-by-default is also a strategy, and a more defensible one for most teams.

#### Architectural implications

- The decision (single-cloud, multi-cloud, hybrid) is made deliberately with documented reasons; defaulting to multi-cloud "for resilience" without specific failure modes in mind is recognised as an anti-pattern.
- When multi-cloud is chosen, the integration boundary is sharply defined — which workloads run where, what crosses the cloud boundary, and the operational cost of that boundary is budgeted.
- Cloud-portable abstractions (Kubernetes, Terraform, OpenTelemetry) reduce the lock-in surface; cloud-specific services (managed databases, AI services) accept the lock-in in exchange for operational savings.

#### Reference

[Corey Quinn — The Multi-Cloud Industry's Inflated Hype](https://www.lastweekinaws.com/) — the industry's most-read sceptical voice on multi-cloud as a default, with practical analysis of when it's actually warranted.

---

### 3. Native services beat self-managed alternatives until they don't

A managed Postgres (RDS, Cloud SQL, Azure Database) costs more per CPU than self-managed Postgres on EC2. The self-managed option looks cheaper until the team computes the operational cost — patching, backups, replication, failover testing, the on-call burden when the database has an issue at 3am. For most workloads, the managed service is cheaper in total cost of operation because the operational savings dwarf the per-CPU premium. The exception is workloads at extreme scale or with specific requirements the managed service doesn't accommodate, where the per-CPU cost actually matters and the team has the depth to operate the alternative competently.

#### Architectural implications

- The default is the managed service; self-managing is justified by specific workload characteristics (extreme scale, custom configuration, cost-at-scale where the premium becomes meaningful).
- Total cost of operation includes engineering time, on-call burden, and the opportunity cost of attention spent on infrastructure rather than product.
- Self-managed services are operated with the same discipline as managed ones — high availability, monitoring, backup verification, disaster recovery — not as an afterthought because "we own it."

#### Reference

[Charity Majors — Use the managed service](https://charity.wtf/2019/02/13/should-i-run-postgres-on-kubernetes/) — a working operator's case for managed services as the default, drawn from experience operating both sides.

---

### 4. Commitment patterns and pricing models are architectural decisions

Cloud pricing is not a flat rate. On-demand instances are the most expensive option; reserved instances or savings plans (committing 1-3 years) discount 40-70%; spot instances offer further 60-90% discounts for interruptible workloads. The architecture determines which pricing model is available — stateless workloads can run on spot; stateful workloads with predictable demand can run on reserved capacity; bursty workloads benefit from on-demand. Treating pricing as procurement's problem and the architecture as engineering's problem leaves significant cost on the table; treating them as joint decisions is what produces the bills cloud architects are proud of.

#### Architectural implications

- Workload characteristics (stateless, predictable, bursty, interruptible) drive pricing-model selection at design time, not as an after-the-fact optimisation.
- Reserved capacity and savings plans are budgeted against forecast load; the commitment is matched to the predictable baseline, with on-demand and spot covering variable load.
- Spot interruption tolerance is built into stateless workloads — graceful shutdown handlers, idempotent processing, work resumption — to make spot pricing accessible.

#### Reference

[AWS Pricing Calculator](https://calculator.aws/) and the [FinOps Foundation Framework](https://www.finops.org/framework/) — the practical and organisational treatments of pricing as part of the architecture.

---

### 5. Identity is the perimeter in cloud architectures

In the data-centre era, the network was the perimeter — the firewall separated trusted from untrusted, and inside the perimeter, things mostly trusted each other. In cloud, the network perimeter is dissolved by definition — services from anywhere can reach anywhere, and "inside the network" no longer means anything. The new perimeter is identity: every action is authenticated by an identity, authorised against policies, and audited by the cloud's IAM. Designing identity well — service principals with least-privilege roles, federated identity from the corporate directory, automatic credential rotation — is the architectural commitment that determines whether the cloud is secure or theatrically secure.

#### Architectural implications

- Every service runs as a specific identity (IAM role, managed identity, service account) with the minimum permissions needed for its job; no shared service accounts, no over-privileged roles "for convenience."
- Human access is federated from the corporate identity provider; long-lived credentials are eliminated in favour of session-based access via SSO and just-in-time elevation.
- Permissions are reviewed regularly (quarterly is reasonable); accumulated privileges from old projects, people who left, services that were retired are pruned.
- Audit logs from cloud-provider IAM (CloudTrail, Activity Log, Cloud Audit Logs) are retained, monitored, and exercised — the questions security and compliance ask are answered from these logs.

#### Reference

[NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — the canonical reference for identity-based perimeter architectures, articulating the principles every cloud security model now embeds.

---

### 6. Cost is a non-functional requirement that requires daily attention

Cloud bills surprise teams when no one is watching them. A development environment left running over the weekend, an unrotated S3 bucket accumulating logs, a queue with no consumer that bills for stored messages, an instance type that was right two years ago and is now 3x more expensive than the current generation — these are continuous leaks, individually small and collectively catastrophic. Treating cost as a daily concern with named ownership, regular reviews, and engineering action items is what keeps cloud bills predictable; treating it as procurement's job lets it grow unbounded between renewals.

#### Architectural implications

- Cost is observed daily — dashboards showing spend by service, by environment, by team — and anomalies trigger investigation, not normalisation.
- Tagging policies are enforced (every resource has owner, environment, project tags) so cost can be attributed; un-tagged resources are flagged or auto-decommissioned.
- Engineering owns cost decisions for the workloads it operates; FinOps provides the visibility and the tooling, engineering applies the changes.
- Architectural reviews include cost projections; the cost of a design is a design property, not a discovery during procurement.

#### Reference

[FinOps Foundation Framework](https://www.finops.org/framework/) — the canonical industry treatment of cloud financial operations as a continuous discipline shared between engineering, finance, and operations.

---

## Architecture Diagram

The diagram below shows a canonical cloud-native architecture: a network perimeter defined by identity rather than IP; managed compute (containers, serverless) running stateless workloads; managed data services holding state; observability, security, and cost as cross-cutting concerns; multi-region deployment for high-availability workloads; spot/reserved capacity matching workload characteristics.

---

## Common pitfalls

### ⚠️ Lift-and-shift as cloud strategy

Moving on-premises servers to cloud VMs without changing the architecture. The team gets cloud bills with on-prem operational characteristics — no elasticity, no managed services, no resilience benefits — at higher cost.

#### What to do instead

Lift-and-shift is a starting point at most. The real work begins after: re-platforming to managed services, refactoring to stateless patterns, adopting cloud-native operational tooling. The gains accrue from these changes, not from the migration itself.

---

### ⚠️ Multi-cloud for resilience without specific failure modes

Operating across hyperscalers "for resilience" without identifying which failures multi-cloud actually mitigates. The team pays the integration cost forever; the imagined resilience benefit rarely materialises because the actual failures (regional outages, application bugs, configuration errors) are not addressed by multi-cloud.

#### What to do instead

Single-cloud by default with strong multi-region resilience. Multi-cloud only for specific reasons — regulatory data residency, genuine vendor risk that's been quantified, best-of-breed services that justify the operational tax.

---

### ⚠️ Self-managed by default

Running Postgres, Kafka, Elasticsearch on EC2 because "we save on the managed service premium." The savings are typically 30-50%; the operational cost is 5-10x once on-call burden, patching, backups, and disaster recovery are honestly accounted for.

#### What to do instead

Managed services by default. Self-managed only at scale where the per-CPU premium becomes meaningful, with a team that has the depth to operate competently — not as a default driven by per-line-item pricing comparison.

---

### ⚠️ IAM by accumulation

Permissions added over time, never removed. Service accounts that were narrow at launch become Swiss Army knives. Roles that "needed full access for a migration" never get scoped back. The blast radius of a compromised credential grows quietly until an incident reveals it.

#### What to do instead

Least privilege as a discipline, with periodic review. Permissions are scoped at creation; expanded only with justification; reviewed quarterly; pruned when projects close or people leave.

---

### ⚠️ Cost as a procurement concern

Engineering owns architecture; procurement owns cost. The bill grows; engineering doesn't see it until renewal. The only lever procurement has is renegotiation, which doesn't address the underlying inefficiency.

#### What to do instead

Cost is an engineering concern with daily visibility. Engineers see their team's spend; anomalies trigger investigation; architectural reviews include cost projections; FinOps provides tooling, engineering applies changes.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Primary cloud choice is documented with team, geography, and tooling considerations ‖ The choice is defensible to a CTO joining in three years; the trade-offs are recorded; secondary clouds (where used) have explicit rationale tied to specific failure modes or capability gaps. | ☐ |
| 2 | Multi-cloud (where adopted) has documented reasons and bounded integration surface ‖ Specific workloads on each cloud; integration boundary is sharp; operational cost of multi-cloud is budgeted, not absorbed silently. | ☐ |
| 3 | Managed services are the default; self-managed alternatives are justified with workload-specific reasons ‖ Total cost of operation includes engineering time and on-call burden; self-managed services are operated with same rigour as managed (HA, monitoring, DR), not casually. | ☐ |
| 4 | Pricing model selection (on-demand, reserved, spot) matches workload characteristics ‖ Stateless/interruptible workloads use spot where viable; predictable baselines covered by reserved/savings plans; on-demand reserved for variable load. The mix is reviewed quarterly. | ☐ |
| 5 | Every workload runs as an identity with least-privilege permissions ‖ Service accounts narrowly scoped; no shared identities; no long-lived "convenience" credentials; permissions reviewed quarterly and pruned as projects close. | ☐ |
| 6 | Human access is federated from the corporate identity provider with SSO and JIT elevation ‖ No long-lived IAM users for humans; cloud console access via SSO; elevated permissions granted just-in-time for the specific task; all sessions logged. | ☐ |
| 7 | Audit logs (CloudTrail, Activity Log, Cloud Audit Logs) are retained, monitored, and exercised ‖ Retention period meets regulatory requirements; alerts on suspicious actions; the team has actually answered security/compliance questions from these logs, not just configured them. | ☐ |
| 8 | Cost is observed daily with attribution to teams and projects ‖ Spend dashboards by service, environment, team; anomalies trigger investigation; tagging policies enforced; un-tagged resources flagged. | ☐ |
| 9 | Architectural reviews include cost projections, not just functional design ‖ Cost is a design property surfaced at decision time; the choice between architectures considers spend at scale; FinOps reviews join engineering reviews for significant changes. | ☐ |
| 10 | The team has a documented disaster-recovery posture for cloud-region failure ‖ Multi-region or multi-zone HA matches RPO/RTO commitments; drills exercise the actual recovery, not just the runbook; the team has done it, not just configured it. | ☐ |

---

## Related

[`technology/api-backend`](../api-backend) | [`technology/databases`](../databases) | [`technology/devops`](../devops) | [`principles/cloud-native`](../../principles/cloud-native) | [`system-design/scalable`](../../system-design/scalable) | [`system-design/ha-dr`](../../system-design/ha-dr)

---

## References

1. [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) — *aws.amazon.com*
2. [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/) — *learn.microsoft.com*
3. [Google Cloud Architecture Framework](https://cloud.google.com/architecture/framework) — *cloud.google.com*
4. [The Twelve-Factor App](https://12factor.net/) — *12factor.net*
5. [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) — *NIST*
6. [FinOps Foundation Framework](https://www.finops.org/framework/) — *finops.org*
7. [Terraform](https://www.terraform.io/) — *terraform.io*
8. [Kubernetes](https://kubernetes.io/) — *kubernetes.io*
9. [Cloud Native Computing Foundation](https://www.cncf.io/) — *cncf.io*
10. [Charity Majors — Use the managed service](https://charity.wtf/2019/02/13/should-i-run-postgres-on-kubernetes/) — *charity.wtf*
