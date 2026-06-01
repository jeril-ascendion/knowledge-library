# ascendion.engineering — Claude session memory

This file is the project memory + index. Standards live in dedicated docs:
- **[DESIGN.md](DESIGN.md)** — visual / diagram / animation / interaction system
- **[CONVENTIONS.md](CONVENTIONS.md)** — content / structure / voice / links
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — human contributor workflow
- Reference exemplars (match these): `/patterns/data/` and `/patterns/integration/`

## Project
Static site generator producing the ascendion.engineering knowledge library.
In production. Knowledge-graph v1.1 work in flight.
- **~31 content sections**, **182 article pages** (taxonomy in `tools/seed_content.py`).
- Build: `python tools/generate.py --src ./content --out ./dist --clean`.

## Conventions (do not violate without asking) — full detail in DESIGN.md / CONVENTIONS.md
- Brand accent: terracotta `#C96330` (chrome). Hero SVGs: 2 colours only —
  warm neutral `#D6D2C8` + terracotta `#C96330`. See DESIGN.md §1.
- Canonical page structure + ADR 10-section structure: CONVENTIONS.md §1.
- Diagram standard (init params, zone colours, group-edges, textContent
  escaping): DESIGN.md §4. One topic-specific diagram per page; Mermaid 10.x.
- Taxonomy in `tools/seed_content.py` is the source of truth; don't rename slugs.
- Substantive practitioner tone, no marketing voice.

## Active work
Knowledge Graph v1.1 — see `docs/v1.1/playbook.md` (EPIC/task breakdown),
`docs/v1.1/spec.md`, prototype at `docs/v1.1/prototype.html`.

## Critical files
- `tools/generate.py` — main generator (~12.8k lines): head/SEO/GA4, TOC +
  floating button + colophon/end-matter, diagram pipeline, AUTHORING
  CONVENTIONS docstring.
- `src/shared.css` — all visual standards (the source; `dist/shared.css` is built).
- `tools/seed_content.py` — TAXONOMY / NESTED_TAXONOMY / SECTIONS.
- `.github/workflows/deploy.yml` — CI.

## Sign-offs locked (v1.1) — do not relitigate without explicit approval
1. Embedding model: bge-small-en-v1.5
2. Chunking: 10 chunks/page including references
3. Section-index pages: yes, third node type
4. Gold-reference summary_author: "Platform Engineering"
5. Adjacent suggestions: top-3, cosine > 0.55
6. HNSW: M=16, ef_construction=200, ef_search=50

## Working preferences
- Iterative architectural discussion before code
- Short bash audits to verify state before each major action
- Clean commits with verified outputs; substantive tone, no marketing voice

## AWS deployment
- Hosted in Ascendion account **852973339602**; S3 `ascendion-engineering-site`,
  CloudFront `E2O2I6L3GV59TM`.
- **Deploy with profile `ascendion-prod`** (sso-session `ascendion`,
  ascendiondigital.awsapps.com). The CLAUDE-documented
  `PowerUserAccess-852973339602` profile is **stale** (its `jeril-ascendion`
  sso-session token expired); `ascendion-prod` reaches the same account/role.
- Deploy = `aws s3 sync dist/ s3://ascendion-engineering-site --delete` (with
  per-type cache headers) + CloudFront invalidation `/*`.

## Learnings / gotchas (durable)
- **Mermaid renders from `.mermaid` `textContent`.** Diagram source must stay
  HTML-entity-escaped (`&lt;b&gt;`) so textContent decodes once to literal
  `<b>`. Unescaping injects real DOM nodes that collapse multi-line labels.
- **A full `--clean` build re-touches every file** → an `aws s3 sync` re-uploads
  all 215 (mtimes change). Re-apply long-cache headers to `assets/og/*` (1yr)
  and SEO files (1day) after the full sync, or they reset to max-age=300.
- **Sitemap ping endpoints are dead** — Google + Bing return 410; submit via
  Search Console / Bing Webmaster Tools instead.
- **Diagram init is duplicated** in every `diagram.mmd` (not centralized) — see
  DESIGN.md §9 "Known drift" for the cleanup backlog.
- GA4 = `G-W7F7SG5F83`, `send_page_view: false`, one manual page_view w/ content_group.
