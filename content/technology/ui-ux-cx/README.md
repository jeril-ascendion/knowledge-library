# UI, UX & CX

**Human-Centric Interfaces — building intuitive digital journeys and seamless user experiences.** The interface is where every architectural choice meets every customer; the work that happens here has to look effortless to be effortless. This page describes how we approach frontend frameworks, user experience design, and the broader customer journey that begins long before a user touches a screen and continues long after they close it.

**Section:** `technology/` | **Subsection:** `ui-ux-cx/`
**Alignment:** React | Angular | Vue.js | Web Vitals

---

## What "UI, UX & CX" actually means

Three layers, often confused, with very different stakes. The *UI* is the surface — the components, the pixels, the framework that renders them. The *UX* is the behaviour — the flows, the affordances, the laws of perception that make a surface feel intuitive or obstructive. The *CX* is the whole journey — the moments before, during, and after a session, across every channel the customer encounters. A team that conflates these layers builds a UI that ships, a UX nobody planned, and a CX that emerges accidentally from whichever channel team shipped last.

Treating them as distinct disciplines — staffed differently, measured differently, governed differently — is what separates an interface that works in a demo from a journey that retains customers. The frameworks (React, Angular, Vue) matter; the design system that scales them matters more; the customer journey that gives them meaning matters most.

---

## Six principles

### 1. Framework choice is a five-year commitment

React, Angular, Vue, and Svelte each carry different ecosystems, hiring profiles, and architectural fits. The choice locks in component libraries, state management patterns, testing tooling, build pipelines, and the talent market the team will hire from for the next half-decade. Picking by team enthusiasm or framework popularity is choosing by criteria that will not matter in three years; the criteria that will matter are ecosystem maturity, enterprise support, the team's current depth, and the integration cost with the rest of the stack.

#### Architectural implications

- The decision is documented with the trade-offs the team accepts (bundle size, learning curve, ecosystem breadth, talent market depth).
- Component patterns and state-management choices are made *with* the framework's idioms, not against them — fighting the framework costs more than the wrong framework would have.
- Migration off a framework is treated as a multi-quarter programme, not a refactor — and is planned only when the trade-offs have shifted enough to justify the cost.

#### Reference

[State of JS Survey](https://stateofjs.com/) — annual industry telemetry on framework adoption, satisfaction, and trajectories that informs the long-horizon view.

---

### 2. Component architecture is the throughput of the UI team

A design system with disciplined component boundaries multiplies a team's velocity; a component soup divides it. The architectural property is not "we have a Storybook"; it is that every component has a single responsibility, a documented contract, predictable composition, and version semantics that allow it to evolve without breaking everything that consumes it. Without this, every new feature pays a tax to navigate, copy, modify, and integrate the existing code; with it, new features compose from existing pieces.

#### Architectural implications

- Components are versioned, documented, and tested in isolation — the design system is a library with a release process.
- Visual regression testing exists for the design system and is part of the merge gate; component changes are caught before they reach product code.
- The boundary between "design system component" and "product component" is explicit; product code does not silently fork the design system.

#### Reference

[Storybook](https://storybook.js.org/) — the canonical tool for isolating, documenting, and testing component contracts; the discipline it enforces is more important than the tool itself.

---

### 3. UX laws are testable hypotheses, not stylistic preferences

Fitts's Law (target acquisition time depends on size and distance), Hick's Law (decision time grows with choice count), Miller's Law (working memory holds about seven items), Jakob's Law (users prefer your site to work like sites they already use) — these are predictions about user behaviour, not aesthetic guidelines. Designs that ignore them produce friction in measurable ways: longer task time, higher error rates, lower completion. Designs that respect them feel "obvious," which is the highest compliment a UX can receive.

#### Architectural implications

- UX decisions reference the laws explicitly when they're at stake; "we made the buttons bigger" becomes "we shortened the Fitts distance for the primary action."
- Friction is measured (time-on-task, error rates, completion) not assumed; the law is the hypothesis, the metric is the test.
- Pattern libraries embed the laws — primary CTAs are sized and positioned for fast acquisition; option lists respect choice limits — so designers don't reinvent these decisions per screen.

#### Reference

[Laws of UX](https://lawsofux.com/) — the canonical catalogue of cognitive and behavioural laws relevant to interface design, with citations to the original research.

---

### 4. Performance is a UX feature, not an engineering nicety

Largest Contentful Paint above 2.5 seconds, Interaction-to-Next-Paint above 200ms, Cumulative Layout Shift above 0.1 — these are not abstract numbers; they are user perceptions of "the site is broken." Core Web Vitals are now Google ranking factors, conversion-rate predictors, and the closest objective measure of UX quality. Treating performance as a feature with its own product owner, budget, and release gate is the difference between a fast site and a site whose performance erodes one PR at a time.

#### Architectural implications

- Performance budgets are documented per page or route — bundle size, image weight, time-to-interactive — and enforced in CI.
- Real-user monitoring (RUM) measures actual user experience, not lab benchmarks; the regression alert is on the 75th-percentile real user, not the median synthetic test.
- Perceived performance (skeleton screens, optimistic UI, progressive enhancement) is part of the design vocabulary, not bolt-on optimisation.

#### Reference

[Web Vitals — web.dev](https://web.dev/articles/vitals) — Google's authoritative reference for the metrics, thresholds, and measurement methodology; informs almost every modern frontend performance practice.

---

### 5. Customer experience is a sequence of moments across channels

A customer journey rarely happens on one screen, in one session, or on one device. It begins with an ad, continues through a search, picks up in an app, pauses at a phone call, resumes in a chat, and concludes with an email. Treating each channel as a separate product produces a fragmented experience where the customer has to re-explain themselves at every boundary. Treating the journey as the unit of design — with handoff semantics, state continuity, and consistent identity across channels — produces a CX that feels like one company instead of seven.

#### Architectural implications

- Customer state (preferences, in-flight transactions, recent context) is centralised and accessible to every channel — not duplicated per channel and silently diverging.
- Journey analytics measure cross-channel paths, not just per-channel funnels; the question "how often do users hand off from app to call centre, and how often does the agent know what the user was doing?" has an answer.
- Channels have explicit handoff contracts: what state transfers, what the new channel can assume, what gracefully falls back when state is unavailable.

#### Reference

[Forrester — Customer Journey Mapping](https://www.forrester.com/blogs/category/customer-journey-mapping/) — the canonical industry treatment of journey analytics as a discipline that crosses channel and team boundaries.

---

### 6. Omnichannel is a content-architecture problem, not a channel problem

The instinct to build "an omnichannel experience" by adding more channels produces an explosion of duplicated content, divergent presentation logic, and brittle integrations. The architectural answer is to invert the structure: a single source of truth for content, products, prices, and rules, with each channel rendering that source contextually. The channels become *views*, not *sources* — and the channel team's job becomes optimising rendering, not reconciling data. Headless CMS, federated commerce, and content APIs are the patterns; the discipline is committing to them before the channel count gets out of hand.

#### Architectural implications

- Content, product, and pricing data have a single source — every channel reads from it, no channel writes back to its own copy.
- Channel-specific presentation logic is isolated; layout, language, and adaptation rules are channel concerns, while the underlying entity definitions are not.
- Adding a new channel costs the rendering effort, not the data-modelling effort — the second new channel is dramatically cheaper than the first.

#### Reference

[MACH Alliance](https://machalliance.org/) — the industry consortium that articulates the Microservices, API-first, Cloud-native, Headless architectural pattern under which modern omnichannel platforms are built.

---

## Architecture Diagram

The diagram below shows the canonical UI/UX/CX architecture: a design system feeding multiple channel renderers; a customer state service that all channels read from and write to; an analytics layer that measures the journey across channels; and a content-and-data backbone that decouples the rendering from the source of truth.

---

## Common pitfalls

### ⚠️ The framework as the architecture

Picking a framework and treating its conventions as the entire architecture. Component boundaries, state shape, and API conventions are inherited from tutorials rather than designed for the product. Three years later, every framework upgrade is a partial rewrite.

#### What to do instead

The framework is a tool; the architecture is a separate decision. Component boundaries, state shape, and integration patterns are designed for the product and documented independently of framework specifics.

---

### ⚠️ Design system that is not a system

A "design system" that is a Figma file plus a Storybook, with neither one canonical and both diverging from production. Designers ship in Figma; developers ship in Storybook; production ships somewhere else. The system has the appearance of consistency without the property.

#### What to do instead

The design system is one source of truth, in code, used in production. Figma references the production tokens; Storybook is the documentation of what's deployed; design and engineering ship from the same artefact.

---

### ⚠️ Performance as an end-of-cycle concern

Performance work happens in the last sprint before launch, when most performance debt has accumulated and is expensive to remove. Wins are localised, regressions return quickly, and the team's perception is "performance is a one-time fix" rather than a continuous discipline.

#### What to do instead

Performance budgets are enforced in CI from day one. Each PR is judged against the budget; regressions are reverted, not negotiated. Performance work is continuous and small, not occasional and large.

---

### ⚠️ Per-channel UX teams in silos

Each channel has its own UX team, its own design language, its own state model. The customer experiences the seams; the company experiences the cost of duplicated work. New customer scenarios that span channels are slow to ship because every channel's team has its own backlog.

#### What to do instead

Journey-centric design with channel-specific delivery. The customer state, terminology, and core flows are owned at the journey level; the channel teams optimise their rendering and channel-specific adaptations within those boundaries.

---

### ⚠️ Omnichannel as an aggregation tax

Adding channels by aggregating per-channel content produces a maintenance burden that grows quadratically. Each new channel multiplies the integration matrix; each content change requires updates in N places.

#### What to do instead

Invert: a single content source, channel-specific renderers. The channel matrix grows linearly because each new channel adds rendering, not data plumbing.

---

## Adoption checklist

|   | Criterion |   |
|---|---|---|
| 1 | Framework choice is documented with five-year trade-offs, not picked by team enthusiasm ‖ Long-horizon criteria — ecosystem, talent, enterprise support, integration — drive the decision; the choice is defensible to a CTO joining in three years. | ☐ |
| 2 | The design system is in code, versioned, and the same artefact used in production ‖ Single source of truth across design and engineering; visual regression testing in CI; component contracts that survive refactors. | ☐ |
| 3 | UX decisions cite the relevant laws when stakes are high ‖ Friction is named (Fitts distance, Hick choice count, Miller chunk size); decisions are testable; pattern libraries embed the laws so they don't get reinvented per screen. | ☐ |
| 4 | Performance budgets are documented per route and enforced in CI ‖ Bundle, image weight, time-to-interactive thresholds; PRs that breach budget are reverted; regressions are caught at merge, not at customer report. | ☐ |
| 5 | Real-user monitoring covers the 75th percentile, not just synthetic ‖ Lab benchmarks lie about real-user experience; RUM at p75 reveals what actual customers see and is the basis for SLO and regression detection. | ☐ |
| 6 | Customer state is centralised and accessible to every channel ‖ One source of identity, preferences, and in-flight context; channels read from it, never silently fork it; handoffs preserve the context the customer just established. | ☐ |
| 7 | Journey analytics span channels, not just funnels per channel ‖ Cross-channel paths are visible; questions like "how often does an in-app session escalate to a call?" have answers backed by data. | ☐ |
| 8 | Content, product, and price are sourced once and rendered per channel ‖ Headless content, federated commerce, channel-specific renderers; new channels cost rendering effort, not data integration effort. | ☐ |
| 9 | Accessibility (WCAG 2.2 AA) is built in, not retrofitted ‖ Components ship accessible by default; audits are part of CI; the legal, ethical, and growth arguments for accessibility are taken as given rather than rediscovered annually. | ☐ |
| 10 | The team has a named owner for performance, accessibility, and journey design ‖ Clear accountability for the cross-cutting concerns that have no natural home; without an owner, all three quietly degrade between releases. | ☐ |

---

## Related

[`technology/api-backend`](../api-backend) | [`technology/cloud`](../cloud) | [`principles/foundational`](../../principles/foundational) | [`patterns/data`](../../patterns/data) | [`patterns/integration`](../../patterns/integration) | [`technology/engagement-models`](../engagement-models)

---

## References

1. [React](https://react.dev/) — *react.dev*
2. [Angular](https://angular.dev/) — *angular.dev*
3. [Vue.js](https://vuejs.org/) — *vuejs.org*
4. [Web Vitals](https://web.dev/articles/vitals) — *web.dev*
5. [Laws of UX](https://lawsofux.com/) — *lawsofux.com*
6. [WCAG 2.2 — W3C](https://www.w3.org/WAI/standards-guidelines/wcag/) — *w3.org*
7. [Material Design 3](https://m3.material.io/) — *material.io*
8. [Storybook](https://storybook.js.org/) — *storybook.js.org*
9. [State of JS Survey](https://stateofjs.com/) — *stateofjs.com*
10. [MACH Alliance](https://machalliance.org/) — *machalliance.org*
