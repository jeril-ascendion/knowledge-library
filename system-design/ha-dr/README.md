# High Availability & DR

> **Section:** `system-design/` | **Subsection:** `ha-dr/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Active-active, active-passive, RTO/RPO targets, failover automation, and disaster recovery playbooks.

This document is part of the **System Design Reference Scenarios** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Eliminate Single Points of Failure

Every component has a backup. If removing one instance causes an outage, it is a SPOF. Load balancers, databases, message brokers, API gateways — all must run in at least two AZs with automatic failover.

### 2. RTO and RPO are Architectural Inputs

Define RTO and RPO before designing the system, not after. They are business requirements that directly determine database replication mode, failover automation, and infrastructure cost. Document them in the NFR catalog.

### 3. Test Failover Paths Continuously

An untested failover path is not a failover path — it is a theoretical one. Automate failover testing in staging (monthly) and run annual production failover drills. Chaos Engineering is not optional for high-availability systems.

### 4. Health Checks Drive Automation

Every component must expose liveness and readiness health endpoints. Orchestrators (Kubernetes, ECS, ALB) use these to automatically remove unhealthy instances from rotation without human intervention.

### 5. Recovery Runbooks Must Be Scripted

Manual recovery procedures with more than five steps will fail under pressure. Automate recovery steps as runbooks (Ansible, SSM Documents, Terraform) that operators can execute with a single command.


---

## Implementation Guide

**Step 1: Define RTO/RPO by System Tier**

Classify systems: Tier 1 (core banking, payments) = RTO 1hr/RPO 15min. Tier 2 (digital channels) = RTO 4hr/RPO 1hr. Tier 3 (analytics, reporting) = RTO 24hr/RPO 4hr. Different tiers justify different architecture and cost.

**Step 2: Identify and Eliminate SPOFs**

Draw the architecture diagram. Circle every component where failure would cause an outage. That is your SPOF inventory. Prioritize elimination by impact: start with the components in every critical path.

**Step 3: Choose the Replication Mode per Component**

Synchronous replication = zero data loss but adds write latency (5–10ms for same-region Multi-AZ). Asynchronous = potential data loss measured by replication lag but no write latency impact. Match to your RPO: zero RPO requires synchronous replication.

**Step 4: Implement Automated Health Check Failover**

Configure Route 53 health checks for DNS failover. Configure ALB target group health checks for application failover. Configure RDS Multi-AZ for database failover. All should be automatic — human-initiated failover adds 15–30 minutes to your RTO.

**Step 5: Run Monthly Chaos Experiments**

Use AWS Fault Injection Simulator, LitmusChaos, or Netflix Chaos Monkey to terminate instances, inject network latency, and simulate AZ failures in staging. Document findings. Fix gaps. Repeat.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| RTO/RPO Defined and Documented | Solution Architect | RTO and RPO defined per system tier in NFR catalog | Required |
| SPOF Inventory Complete | Solution Architect | All SPOFs identified and remediation plan in place | Required |
| Multi-AZ Deployment Verified | Platform Engineer | All Tier 1 components deployed across minimum 2 AZs | Required |
| Failover Tested and Documented | SRE / DR Lead | Automated failover tested; actual RTO/RPO measured and within targets | Required |
| DR Drill Results Submitted to BSP | Technology Risk Officer | Annual DR drill results documented and submitted (BSP requirement) | Required |


---

## Recommended Patterns

### Active-Active Multi-AZ

Application servers in all AZs serve live traffic behind a load balancer. Database uses synchronous Multi-AZ replication with automatic failover. Zero RTO for AZ failures. The standard pattern for 99.99% availability.

### Active-Passive Multi-Region

Primary region serves all traffic. DR region runs a warm standby with replicated data. Route 53 failover routing activates the DR region when primary health checks fail. Achieves RTO of 5–15 minutes with full automation.

### Pilot Light

A minimal version of the DR environment runs continuously (databases replicated, AMIs current). During failover, scale up the DR environment to full production size. Lower cost than warm standby, higher RTO (30–60 minutes).

### Backup and Restore

The simplest DR approach: automated backups to S3, with restore procedures documented and tested. Appropriate for Tier 3 systems. RTO measured in hours; RPO equal to backup frequency.


---

## Anti-Patterns to Avoid

### ⚠️ Untested DR Plans

A DR plan that has never been executed is a fiction. The most common finding in post-incident reviews: 'We had a DR plan but when we tried to execute it, we discovered it was outdated and incomplete.' Test quarterly.

### ⚠️ Symmetric RTO/RPO for All Systems

Setting the same aggressive RTO/RPO for every system drives unnecessary cost for non-critical systems while the budget is diluted away from genuinely critical ones. Tier your systems by business impact.


---

## AI Augmentation Extensions

### AI-Assisted Chaos Experiment Design

LLM agents analyze system architecture diagrams and generate a targeted chaos experiment plan — identifying which failure injection scenarios would most effectively validate HA/DR designs based on the specific topology.

> **Note:** AI-generated chaos plans are starting points. Have your SRE team review and adjust blast radius before executing any experiment in staging.

### Automated DR Drill Documentation

After each DR drill, AI agents parse structured test results, compare actual RTO/RPO against targets, generate the drill report in BSP-required format, and flag gaps needing remediation.

> **Note:** DR drill reports submitted to BSP must be reviewed and signed by the Technology Risk Officer before submission.


---

## Related Sections

[`nfr/reliability`](../nfr/reliability) | [`observability/sli-slo`](../observability/sli-slo) | [`runbooks/rollback`](../runbooks/rollback) | [`compliance/bsp-afasa`](../compliance/bsp-afasa) | [`infra/resilience`](../infra/resilience)

---

## References

1. [Site Reliability Engineering — Google](https://sre.google/sre-book/table-of-contents/) — *sre.google*
2. [Designing Distributed Systems — Brendan Burns](https://www.oreilly.com/library/view/designing-distributed-systems/9781491983638/) — *O'Reilly*
3. [AWS Well-Architected Framework — Amazon Web Services](https://aws.amazon.com/architecture/well-architected/) — *aws.amazon.com*
4. [BSP Circular 982 — Technology Risk Management](https://www.bsp.gov.ph/Regulations/IssuancesAmendments/2017/c982.pdf) — *bsp.gov.ph*
5. [Building Evolutionary Architectures — Ford, Parsons, Kua](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/) — *O'Reilly*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `system-design/ha-dr/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
