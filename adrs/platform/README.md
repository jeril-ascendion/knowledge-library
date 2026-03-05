# Platform ADRs

> **Section:** `adrs/` | **Subsection:** `platform/`  
> **Alignment:** TOGAF ADM | NIST CSF | ISO 27001 | AWS Well-Architected | AI-Native Extensions

---

## Overview

Decisions about platform selection: cloud provider, container orchestration, API gateway, service mesh.

This document is part of the **Architecture Decision Records** body of knowledge within the Ascendion Architecture Best-Practice Library. It provides comprehensive, practitioner-grade guidance aligned to industry standards and extended for AI-augmented, agentic, and LLM-driven design contexts.

---

## Core Principles

### 1. Intentional Design for Platform ADRs

Every aspect of platform adrs must be deliberately designed, not discovered after deployment. Document design decisions as ADRs with explicit rationale.

### 2. Consistency Across the Portfolio

Apply platform adrs practices consistently across all systems. Inconsistent application creates governance blind spots and makes incident investigation unpredictable.

### 3. Alignment to Business Outcomes

Platform ADRs practices must demonstrably contribute to business outcomes: reduced downtime, faster delivery, lower operational cost, or improved compliance posture.

### 4. Evidence-Based Quality Assessment

Quality of platform adrs implementation must be measurable. Define specific metrics and collect evidence continuously — not only at audit or review time.

### 5. Continuous Evolution

Standards for platform adrs evolve as technology and threat landscapes change. Schedule quarterly reviews of applicable standards and update practices accordingly.


---

## Implementation Guide

**Step 1: Current State Assessment**

Document the current state of platform adrs practice: what is implemented, what is missing, what is inconsistent across teams. Use the governance/scorecards section for a structured assessment framework.

**Step 2: Gap Analysis Against Standards**

Compare current state against the standards in this section and applicable frameworks (MADR Format — adr.github.io, Architecture Decision Records — Michael Nygard). Prioritize gaps by business impact and remediation effort.

**Step 3: Design the Target State**

Define the target platform adrs state: which patterns will be adopted, which anti-patterns eliminated, which governance mechanisms introduced. Express as a time-bound roadmap.

**Step 4: Incremental Implementation**

Implement platform adrs improvements incrementally: pilot with one team or system, measure outcomes, refine the approach, then expand. Avoid big-bang transformations.

**Step 5: Validate and Iterate**

Measure the impact of implemented changes against defined success criteria. Incorporate lessons learned into the practice standards. Contribute improvements back to this library.


---

## Governance Checkpoints

| Checkpoint | Owner | Gate Criteria | Status |
|---|---|---|---|
| Current State Documented | Solution Architect | Platform ADRs current state assessment completed and reviewed | Required |
| Gap Analysis Reviewed | Architecture Review Board | Gap analysis reviewed and prioritization approved | Required |
| Implementation Plan Approved | Enterprise Architect | Target state and roadmap approved by ARB | Required |
| Quality Metrics Defined | Solution Architect | Measurable success criteria defined for platform adrs improvements | Required |


---

## Recommended Patterns

### Reference Architecture Adoption

Start from an established reference architecture for platform adrs rather than designing from scratch. Adapt to organizational context rather than rebuilding proven foundations.

### Pattern Library Contribution

When your team solves a recurring platform adrs problem with a novel approach, document it as a pattern for the library. This compounds organizational knowledge over time.

### Fitness Function Testing

Encode platform adrs standards as automated architectural fitness functions — tests that run in CI/CD and fail builds when standards are violated. This makes governance continuous rather than periodic.


---

## Anti-Patterns to Avoid

### ⚠️ Standards Theater

Documenting platform adrs standards in architecture policies that no one reads and no one enforces. Standards without automated validation or governance gates are not operational standards.

### ⚠️ Copy-Paste Architecture

Adopting another organization's platform adrs patterns wholesale without adapting to organizational context, team capability, or regulatory environment. Always adapt; never just copy.


---

## AI Augmentation Extensions

### AI-Assisted Standards Review

LLM agents analyze design documents against platform adrs standards, generating structured gap reports with cited evidence and suggested remediation approaches.

> **Note:** AI review accelerates governance but does not replace expert architectural judgment. Use as a first-pass filter before human review.

### RAG Integration for Platform ADRs

This section is optimized for vector ingestion into an AI-powered architecture assistant. Semantic search enables architects to retrieve relevant platform adrs guidance through natural language queries.

> **Note:** Reindex the vector store whenever section content is updated to ensure retrieved guidance reflects current standards.


---

## Related Sections

[`principles/foundational`](../principles/foundational) | [`patterns/structural`](../patterns/structural) | [`governance/review-templates`](../governance/review-templates) | [`adrs/platform`](../adrs/platform)

---

## References

1. [MADR Format — adr.github.io](https://adr.github.io/madr/) — *adr.github.io*
2. [Architecture Decision Records — Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — *cognitect.com*
3. [RFC Process — IETF](https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=RFC+Process+%E2%80%94+IETF) — *IEEE Xplore*
4. [TOGAF Architecture Decision Log](https://pubs.opengroup.org/architecture/togaf9-doc/arch/) — *opengroup.org*
5. [Documenting Software Architectures — Bass, Clements, Kazman](https://www.amazon.com/Documenting-Software-Architectures-Views-Beyond/dp/0321552687) — *Amazon*
6. [Building Evolutionary Architectures — Ford, Parsons, Kua](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/) — *O'Reilly*


---

*Last updated: 2025 | Maintained by: Ascendion Solutions Architecture Practice*  
*Section: `adrs/platform/` | Aligned to TOGAF · NIST · ISO 27001 · AWS Well-Architected*
