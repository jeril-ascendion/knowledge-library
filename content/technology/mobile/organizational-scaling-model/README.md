# Organizational Scaling Model

> **Section:** `technology/mobile/organizational-scaling-model/`
> **Alignment:** Team Topologies | Inverse Conway Maneuver | DORA | Spotify Squad Model
> **Audience:** Engineering Managers · CTOs · Solutions Architects · People Leaders

The organisational structure of the mobile engineering function determines the architecture of the mobile application — Conway's Law is not a theory, it is an observable empirical regularity. When the mobile engineering function grows from three engineers to fifty, the coordination mechanisms, team boundaries, and knowledge sharing structures that worked at three create bottlenecks at fifty. The Organizational Scaling Model provides a deliberate scaling path aligned with the Scalability Evolution Model (Section 12).

## Overview

The scaling model defines four organisational configurations corresponding to the four engineering growth stages. Each configuration defines team topology, coordination mechanisms, knowledge management approach, and the technical boundaries that encode the organisational structure.

## Organisational Configurations

### Configuration 1: Founding Team (3-8 Engineers)
Single cross-functional team owning the entire mobile codebase on both Android and iOS. Strong pair programming and informal knowledge sharing. Architecture decisions made by the whole team. Code review involves everyone. Daily standups with full context. Technical debt is visible because everyone works in the same codebase.

Risks at this stage: all architectural knowledge concentrated in one or two senior engineers (bus factor). Mitigations: Architecture Decision Records (ADRs) for every significant decision, architecture diagrams maintained as living documentation in the repository, no tribal knowledge.

### Configuration 2: Feature Teams (8-20 Engineers)
2-4 cross-functional feature teams, each owning one or more product feature areas. Feature teams include Android engineers, iOS engineers, and a QA engineer. A platform/infrastructure team (2-3 engineers) owns CI/CD, shared libraries, and architectural standards. Weekly cross-team architecture sync: 30 minutes, rotating facilitator, ADR review and architectural decision-making. Feature teams are autonomous within their module boundaries — they do not require platform team approval for feature work.

### Configuration 3: Product Streams (20-60 Engineers)
Product stream alignment: each stream corresponds to a business domain (Accounts, Payments, Onboarding). Each stream has a Stream Lead (architect-level) who coordinates engineering across the stream's modules. Platform Engineering team (4-6 engineers) owns the golden path, shared infrastructure, and DevOps. Architecture Guild (2 hours per fortnight): stream leads, platform engineers, and rotating feature engineers. Guild produces architectural standards and reviews proposed deviations.

### Configuration 4: Platform Engineering Model (60+ Engineers)
Multiple product lines sharing a common mobile platform. Platform team (8-12 engineers) owns the mobile platform SDK consumed by all product lines. Each product line has an Architect who maintains alignment with platform standards. Inner source model: product line engineers contribute to the platform through pull requests reviewed by the platform team. Platform team runs office hours for architectural consultation.

## Knowledge Management

At every scale level, knowledge must be externalised from individuals into artefacts:
- Architecture Decision Records for every significant architectural choice
- Architecture diagrams maintained in the repository (not in personal wikis or Confluence pages that become stale)
- Internal tech talks: monthly, 30 minutes, rotating engineers presenting a pattern, a library, or a lesson from a production incident
- Onboarding documentation: a new engineer should be productively contributing within 5 business days. If they cannot, the documentation is insufficient.

## Anti-Patterns to Avoid

> **⚠ Hero Engineering** — All architectural knowledge concentrated in one senior engineer. When that engineer leaves, architecture decisions become unclear and consistency degrades.
> **CORRECT:** ADR discipline from day one. Architecture is documented in the repository, not carried in someone's head. When the hero leaves, the ADRs remain.

> **⚠ Conway's Law Ignored** — Two teams sharing ownership of a single module, producing merge conflicts that become architectural conflicts.
> **CORRECT:** Inverse Conway Maneuver: design the module boundaries to match the desired team boundaries before assigning ownership. Module ownership is one-to-one with team ownership.

## References

1. Skelton, Matthew and Pais, Manuel — Team Topologies. IT Revolution Press, 2019.
2. Forsgren et al. — Accelerate. IT Revolution, 2018.
3. Conway, Melvin — How Do Committees Invent? Datamation, 1968.
4. Spotify — Scaling Agile at Spotify. (Kniberg and Ivarsson, 2012)
