# CONVENTIONS.md — Content & Structure Standards

How every **content page** on ascendion.engineering is structured and written.
Visual/diagram/interaction standards live in [DESIGN.md](DESIGN.md); durable
project facts and locked decisions live in [CLAUDE.md](CLAUDE.md); the
human contributor workflow lives in [CONTRIBUTING.md](CONTRIBUTING.md).

> **Reference exemplars** — match these exactly:
> - https://ascendion.engineering/patterns/data/index.html
> - https://ascendion.engineering/patterns/integration/index.html
>
> The enforced source of these rules is the `tools/generate.py` module
> docstring ("AUTHORING CONVENTIONS") plus `verify_link_security()`. This file
> restates them for governance.

---

## 1. Canonical page structure (substantive content pages)

Markdown order, top to bottom — as seen in both exemplars:

```markdown
# Page Title
A one-line description paragraph (becomes the hero subtitle).

**Section:** `<section>/` | **Subsection:** `<subsection>/`
**Alignment:** Standard 1 | Standard 2 | Standard 3 | Standard 4

---

## What "X" actually means          ← definitional opening
## Six principles                    ← exactly 6 numbered flip cards
## Architecture Diagram              ← heading + intro + the diagram
## Common pitfalls when adopting X   ← ~5 ⚠ / CORRECT flip cards
## Adoption checklist                ← ~10 rows
## Related                           ← 4–6 sister-page chips
## References                        ← numbered, every claim hyperlinked
```

Rules:
- **Title** = first `# ` line. **Description** = first non-heading line after it.
- **Tags** = the `**Alignment:**` line (pipe-separated standards/frameworks).
- The generator strips the `Section`/`Alignment`/`Audience` metadata block from
  the body (it becomes hero chips), so keep it in that exact form.
- A page without a topic-relevant diagram **or** with no cited sources is a
  **stub**, regardless of word count.

### ADR pages (the `adrs/` section) use a different canonical structure
10 sections, in order:

```
## ADR Metadata        (pipe table)
## Executive Summary   (opens with **Decision:** …)
## Decision Drivers    (Priority | Quality Attribute | Weight | Rationale)
## Considered Options  (each scored, e.g. 4.83 / 5.0)
## Decision
## Trade-off Analysis  (Trade-off | Consequence | Mitigation)
## Implementation Guidance   (numbered)
## Compliance Checkpoints    (Checkpoint | Trigger | Owner | SLA)
## Related ADRs
## References
```
ADR H1 begins with `ADR: `. ADR pages get the governance colophon end-matter
(not the generic one).

---

## 2. Anti-patterns format

Each anti-pattern is a blockquote pair:

```markdown
> **⚠ [The mistake]** — what goes wrong and why engineers fall into it.
> **CORRECT:** the right approach — specific, implementable, named tech.
```

Topic-specific only. No generic filler. (On non-ADR pages the section is
"Common pitfalls when adopting X"; ADR/mobile pages use "Anti-Patterns to
Avoid" — both use the `⚠ / CORRECT:` blockquote pair.)

---

## 3. Voice & quality bar

Write for **fellow engineers**, not novices. A page is complete when it:

| Criterion | Why |
|---|---|
| Distinguishes the topic from adjacent topics | No content overlap |
| Has a stable point of view | The site takes positions, isn't a wiki mirror |
| Includes a topic-relevant diagram | Visual reasoning is part of the craft |
| Cites standards/sources at every claim | Defensibility |
| Includes pitfalls / anti-patterns | Real practitioner experience |
| Reads in a practitioner voice | Audience = engineers who know the area |

- **No repetition across pages.** Each page owns its concept; cross-reference
  rather than restate (use `## Related` chips + inline links).
- **Stub prose is lorem ipsum.** For a stub, only the title + taxonomy
  placement are committed — rewrite the body freely.

---

## 4. Links & references

- **Every URL must be `https://`** (the build **halts** on any `http://` or a
  domain on the `KNOWN_INSECURE_DOMAINS` blocklist — see
  `verify_link_security()`).
- References are a **numbered list**, every external claim hyperlinked.
- Bare reference URLs are auto-linked by the generator; internal cross-links
  (ADR codes, key section names, OWASP/TOGAF/etc.) are auto-linked once per page.

---

## 5. Information architecture

- One folder per topic: `content/<section>/<subsection>/README.md`
  (+ optional `diagram.mmd`, `hero.svg`).
- Taxonomy is the single source of truth in `tools/seed_content.py`
  (`TAXONOMY`, `NESTED_TAXONOMY`, `SECTIONS`). Orphan folders not in the
  taxonomy are skipped.
- Adding/removing a subsection auto-updates the parent index + home page.
- Taxonomy changes (new section, restructure) require an issue first — they
  affect navigation and need a coordinated update.

---

## 6. What NOT to do

- Don't edit `dist/` (build artefact) or upload directly to S3.
- Don't reuse a generic flowchart as a placeholder diagram — an empty slot is
  more honest than a misleading one.
- Don't restate another page's content.
- Don't add a second accent colour or break the hero 2-colour rule (see DESIGN.md).
- Don't ship `http://` links — the build will fail.

---

*Build: `python tools/generate.py --clean` → verify against the two reference
exemplars → PR. Deploys trigger on push to `main`.*
