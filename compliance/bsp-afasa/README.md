# BSP / AFASA (Philippines)

> **Section:** `compliance/` | **Subsection:** `bsp-afasa/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Bangko Sentral ng Pilipinas circulars, AFASA compliance, DITO/DICT alignment for Philippine financial systems.

This document is part of the **Compliance & Regulatory Frameworks** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Compliance as Architecture Input, Not Output

BSP requirements are architecture constraints to be modeled in the design phase — not audit findings to be remediated after deployment. RTO/RPO, data residency, and audit trail requirements are first-class NFRs.

### 2. Evidence-First Architecture

Every architecture decision with compliance implications must produce auditable evidence: documented DR test results, SIEM alert logs, access control configurations, and architecture diagrams. BSP examiners evaluate documentation quality, not intentions.

### 3. Defense in Depth Satisfies Multiple Circulars

A layered security architecture (network segmentation + application-level controls + monitoring + incident response) simultaneously satisfies requirements across Circular 982 (security controls), Circular 1169 (incident detection), and PCI DSS (for card-issuing banks). Design once, satisfy many.

### 4. Data Residency is Non-Negotiable for PII

Customer financial data (account balances, transaction history, KYC documents) for Philippine residents must remain within Philippine jurisdiction unless BSP grants explicit written approval. Design the data classification and residency architecture before selecting cloud providers.


---

## Implementation Guide

**Step 1: Map Applicable BSP Circulars to Architecture Requirements**

Create a compliance matrix: list each applicable circular, extract the specific architecture requirements from each, and map to the architectural component responsible for satisfying it. This becomes your compliance design specification.

**Step 2: Establish the Technology Risk Register**

Document every technology risk (cyber threats, vendor concentration, technology obsolescence, single points of failure) with: risk description, likelihood (1-5), impact (1-5), risk score, control owner, control effectiveness, residual risk, and review date. Review quarterly with the Technology Risk Officer.

**Step 3: Design the BC/DR Architecture Against RTO/RPO**

For each Tier 1 system, design the recovery architecture to meet RTO ≤ 4 hours and RPO ≤ 2 hours. Document the specific recovery procedure (runbook), the failover trigger (manual vs. automated), and the data replication mode (synchronous vs. asynchronous) that enables the RPO.

**Step 4: Deploy SIEM with BSP Circular 1169 Playbooks**

Implement SIEM with detection rules aligned to BSP Circular 1169 reportable incident categories: unauthorized access, data exfiltration, DDoS, ransomware. For each rule: detection logic, alert severity, response playbook, and escalation path to the Technology Risk Officer for 2-hour reporting compliance.

**Step 5: Prepare the BSP Examination Evidence Repository**

Maintain a continuously updated documentation repository accessible to BSP examiners: architecture diagrams (updated quarterly), technology risk register (updated monthly), DR drill reports (annual), penetration test reports (annual), policy and procedure documents, and access control configurations.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| BSP Circular 982 Controls Mapped | Technology Risk Officer | All TRM controls mapped to implementing architecture components | Required |
| Technology Risk Register Current | Technology Risk Officer | Register updated within last 30 days | Monthly |
| BC/DR Drill Completed | DR Lead / Technology Risk Officer | Annual drill conducted with actual RTO/RPO measured and documented | Annual |
| SIEM Incident Detection Tested | Security Operations | 2-hour detection and reporting capability tested for each Circular 1169 category | Quarterly |
| BSP Examination Evidence Package Ready | Enterprise Architect | All evidence categories current and organized for examiner access | Pre-Examination |


---

## Recommended Patterns

### Compliance-as-Code

BSP architectural requirements expressed as automated tests and policy rules (OPA, AWS Config Rules, Azure Policy). Drift from compliant configuration triggers automated alerts. Evidence is generated automatically by CI/CD pipelines, not assembled manually before examinations.

### Dual-Site Synchronous Replication

Primary data center in Metro Manila + DR site in Cebu or Clark, connected via dedicated MPLS or fiber. Synchronous database replication achieves RPO ≈ 0 for core banking. Annual failover drill with documented RTO measurement. The standard HA/DR architecture for Tier 1 BSP-regulated systems.

### Regulatory Reporting Pipeline

Automated data pipeline that generates BSP-mandated reports (CITEM reports, CAR, SES, DOSRI, ROE) from core banking data sources on the required regulatory schedule, with data lineage documentation satisfying BSP audit requirements.


---

## Anti-Patterns to Avoid

### ⚠️ Manual BSP Compliance Reports

Generating BSP regulatory reports manually from spreadsheets assembled by querying multiple systems. Prone to errors, inconsistencies, and delayed submission. BSP examiners increasingly expect automated, auditable data pipelines for supervisory reporting.

### ⚠️ Data Residency by Trust

Assuming that cloud providers will honor data residency commitments without technical enforcement. Apply AWS Service Control Policies, Azure Policy, or GCP Organization Policies to technically prevent data from being stored outside approved regions — auditable evidence of residency enforcement.

### ⚠️ BC/DR Plan Without Test Results

Maintaining a BC/DR plan document that has never been executed. BSP examination finding #1: 'The institution's BC/DR plan has not been tested within the required annual timeframe.' Untested plans are a Critical Finding.


---

## AI Augmentation Extensions

### AI-Assisted Regulatory Monitoring

Agents monitor BSP issuance announcements and automatically map new circulars to the existing compliance matrix, identifying gaps that require architecture changes and generating impact assessment drafts for the Technology Risk Officer's review.

> **Note:** New BSP requirements must be reviewed by a qualified compliance officer and legal counsel before being added to the architecture implementation backlog. AI mapping is a starting point, not a final determination.

### Automated Evidence Package Generation

Before each BSP examination, AI agents compile the evidence repository: pull the latest architecture diagrams from the documentation system, extract the most recent technology risk register, aggregate DR drill reports, and generate an examination-ready package with a table of contents aligned to the examination scope.

> **Note:** Evidence packages require review and sign-off by the Technology Risk Officer before submission to BSP examiners.


---

## Related Sections

[`compliance/iso27001`](../compliance/iso27001) | [`compliance/pci-dss`](../compliance/pci-dss) | [`security/cloud`](../security/cloud) | [`system-design/ha-dr`](../system-design/ha-dr) | [`governance/roles`](../governance/roles)

---

## References

1. [BSP Circular 982 — Technology Risk Management](https://www.bsp.gov.ph/Regulations/IssuancesAmendments/2017/c982.pdf) — *bsp.gov.ph*
2. [BSP Circular 1169 — Cybersecurity Incident Reporting](https://www.bsp.gov.ph/Regulations/IssuancesAmendments/2022/c1169.pdf) — *bsp.gov.ph*
3. [BSP Manual of Regulations for Banks — IT Standards](https://www.bsp.gov.ph/RegulationsLaws/MORB/MORB.pdf) — *bsp.gov.ph*
4. [Philippines Data Privacy Act (DPA) — Republic Act 10173](https://www.privacy.gov.ph/data-privacy-act/) — *privacy.gov.ph*
5. [AFASA Framework — Bangko Sentral ng Pilipinas](https://www.bsp.gov.ph/) — *bsp.gov.ph*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `compliance/bsp-afasa/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
