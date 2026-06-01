# DESIGN.md — Ascendion Engineering Design System

Single source of truth for the **visual, diagram, animation, and interaction**
standards of ascendion.engineering. Content/authoring rules live in
[CONVENTIONS.md](CONVENTIONS.md); durable project facts live in
[CLAUDE.md](CLAUDE.md).

> **Reference exemplars** — when in doubt, match these two pages exactly:
> - https://ascendion.engineering/patterns/data/index.html
> - https://ascendion.engineering/patterns/integration/index.html
>
> They show the canonical page in its finished state: hero + animated SVG,
> 12-section body, six principle flip-cards, one topic diagram, pitfall
> flip-cards, adoption checklist, related chips, hyperlinked references,
> "On This Page" TOC, floating TOC button, and article end-matter.

The **enforced** source of these values is code:
`src/shared.css` (visual) and `tools/generate.py` (structure, diagrams,
components, SEO, analytics). This file documents them so they can be
governed without reading code. When you change a value here, change it in
the code too (and ideally centralize it — see "Known drift").

---

## 1. Colour

### 1.1 Site palette (CSS custom properties — `src/shared.css :root`)

| Token | Value | Use |
|---|---|---|
| `--bg` | `#FFFFFF` | Page background |
| `--bg-subtle` | `#F9F8F6` | Cards, TOC, code, zebra rows |
| `--ink` | `#0E0E0E` | Primary text |
| `--ink-2` | `#3C3C3C` | Body copy |
| `--ink-3` | `#6E6E6E` | Secondary text |
| `--ink-4` | `#B0B0AA` | Muted labels |
| `--border` | `#E8E8E4` | Hairline borders |
| `--border-md` | `#C4C4BE` | Stronger borders |
| `--accent` | `#C96330` | **Terracotta — the one brand accent** |
| `--nav-bg` | `#0E0E0E` | Sticky nav + floating button bg |
| `--nav-text` | `rgba(255,255,255,0.58)` | Nav links |
| `--nav-hover` | `#FFFFFF` | Nav hover |

**Rule:** terracotta `#C96330` is the only accent. Everything else is
neutral ink/paper. Do not introduce a second accent hue in chrome.

### 1.2 Hero SVG animation palette (STRICT 2-colour rule)

Hero animations (`hero.svg`, the inline SVG library in `generate.py`) use
**only two colours**:

| Colour | Value |
|---|---|
| Warm neutral | `#D6D2C8` |
| Terracotta | `#C96330` |

No other fills/strokes in hero SVGs. (This is the "2-colour palette" rule
referenced in CLAUDE.md — it applies specifically to hero animations, not
to diagrams or chrome.)

### 1.3 Diagram zone palette (Mermaid)

Diagrams use an AWS-style colour-coded-zone convention. Each architectural
zone gets one hue (fill / stroke / text):

| Zone meaning | Fill | Stroke | Text |
|---|---|---|---|
| Presentation / App / client | `#DBEAFE` / `#BFDBFE` | `#2563EB` | `#1e3a5f` |
| Domain / backend services | `#DCFCE7` / `#BBF7D0` / `#86EFAC` | `#16A34A` | `#14532D` |
| Data / BFF / infra adapters | `#FEF9C3` / `#FDE68A` | `#CA8A04` / `#D97706` | `#713f12` / `#78350F` |
| Security | `#FEE2E2` / `#FCA5A5` | `#DC2626` | `#7f1d1d` |
| Testing / verification | `#F3E8FF` / `#E9D5FF` | `#7C3AED` | `#4C1D95` |
| CI/CD / pipeline / neutral | `#E5E7EB` / `#D1D5DB` / `#6B7280` | `#4B5563` | `#111827` |

Diagram theme tokens also exist as `--dg-*` in `:root` (light Figma-style:
`--dg-bg #F4F7FB`, `--dg-stroke #4A72A8`, etc.) for the diagram container.

---

## 2. Typography

| Token | Value |
|---|---|
| `--font` (sans, default) | `'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif` |
| `--mono` | `'IBM Plex Mono', 'Courier New', monospace` |

- Base body font size: **18px** (see generator header note).
- Mono is used for: labels/tags, TOC numbers, colophon keys, end-matter tag,
  breadcrumb-ish microcopy, code.
- Headings: `<h2>` carries a bottom hairline border + generous top margin;
  `<h3>` lighter. (See `.article-body h2/h3` in `shared.css`.)
- Reading column width: `--prose 880px`; max chrome width: `--max 1140px`.

---

## 3. Layout & spacing

| Token | Value | Meaning |
|---|---|---|
| `--max` | `1140px` | The ONE shell width used everywhere |
| `--prose` | `880px` | Article reading column |
| `--r` | `6px` | Default radius |
| `--r-lg` | `10px` | Large radius (cards, diagram-wrap) |
| `--t` | `0.18s ease` | Standard transition |

- Sticky nav height: **58px** (`.nav { position: sticky; height: 58px }`).
- **Scroll offset for anchors:** `html { scroll-padding-top: 88px }` and
  `scroll-margin-top: 88px` on `.article-body h1–h4[id]`, `.adr-toc`,
  `.article-toc` — so anchor jumps clear the sticky nav.
- One page chrome: header (sticky, dark) → hero → article shell → footer.
  The generator owns all chrome; authors write only the body.

---

## 4. Diagrams (Mermaid)

Every `diagram.mmd` is topic-specific and uses the **standard init header**:

```
%%{init:{'theme':'base','themeVariables':{'fontSize':'14px',
'fontFamily':'IBM Plex Sans, system-ui','primaryColor':'#DBEAFE',
'primaryTextColor':'#1e3a5f','primaryBorderColor':'#2563EB',
'lineColor':'#374151','clusterBkg':'#F9FAFB','clusterBorder':'#D1D5DB',
'edgeLabelBackground':'#FFFFFF'},'flowchart':{'curve':'orthogonal',
'padding':30,'nodeSpacing':65,'rankSpacing':75,'useMaxWidth':true}}}%%
```

Standard parameters:

| Param | Value | Notes |
|---|---|---|
| `fontSize` | **14px** default; **16px** for dense/architecture diagrams | Bump to 16px when text is small at 100% zoom |
| `fontFamily` | `IBM Plex Sans, system-ui` | |
| `curve` | `orthogonal` | Right-angle edges only |
| `padding` | `30` (up to `36` for large) | |
| `nodeSpacing` | `60–65` | |
| `rankSpacing` | `75–80` | |
| `useMaxWidth` | `true` | Scales to container |

Diagram authoring rules:
- **Colour-code by zone** using §1.3. Style both the subgraph and its nodes.
- **Prefer `LR` for wide multi-zone diagrams** so zones share horizontal space;
  `TD` for layered/flow diagrams.
- **Group-level edges over individual edges.** If every node in zone A links
  to every node in zone B, draw one `A --> B` (or `subgraph --> subgraph`)
  edge labelled with the relationship — never N×M crossing arrows.
- **Rich labels:** `<b>Title</b><br/>line 2<br/><i>note</i>`. Use `&lt;` /
  `&gt;` for literal angle brackets (e.g. `Result&lt;T, Error&gt;`).
- Keep nodes per zone small enough to read at 100% zoom (≤ ~5).

### How diagrams render (critical implementation note)
Mermaid reads each `.mermaid` element's **`textContent`**. The generator
HTML-escapes diagram source (`& < >` → entities) so `textContent` decodes
**once** back to the intended string (`&lt;b&gt;` → literal `<b>` for
htmlLabels). **Never unescape diagram source into the div** — that injects
real `<b>`/`<br/>` DOM nodes which `textContent` strips, collapsing every
multi-line label. (See `render_mermaid_blocks` and the diagram-wrap path.)

### Diagram container (`.diagram-wrap` / `.article-body pre:has(.mermaid)`)
`background #F8F9FA · 1px #DEE2E6 · radius 10px · padding 2.5rem 2rem ·
min-height 380px · centred · overflow-x auto`. `.mermaid` inside:
`width 100% · min-width 640px · font-size 16px`.

---

## 5. Animation

- **Hero SVGs:** SMIL only — `animate`, `animateTransform`
  (`type=rotate|translate`), `stroke-dasharray`, `opacity`. **No
  `animateMotion` / `mpath`** (unreliable cross-browser). Two-colour palette
  (§1.2). Each new page must invent a *new* visual mechanic — do not reuse
  another page's hero animation concept.
- **UI transitions:** `--t` (0.18s ease) for hovers; floating button uses
  250ms opacity/transform; respect reduced-motion where added.
- **Mermaid:** static render; no diagram animation.

---

## 6. Interaction components (generator-owned, behavior standards)

| Component | Where | Behavior |
|---|---|---|
| **Sticky nav** | every page | dark `#0E0E0E`, 58px, brand + section links + Knowledge Graph / All Topics CTAs |
| **Hero** | every article | breadcrumb (`Home › Section › [Sub] › Title`) + H1 + 1–2 sentence desc (≤400 chars, sentence boundary, **no ellipsis**) + tag chips + animated SVG |
| **On This Page TOC** | non-ADR articles ≥3 H2 | `.article-toc`, `id=on-this-page`, two-column, terracotta row numbers; row number is the position indicator — heading number prefixes (`1. `) are stripped from TOC text |
| **Table of Contents** | ADR articles | `.adr-toc`, `id=table-of-contents`, label "Table of Contents" |
| **Floating TOC button** | all articles | fixed bottom-right; appears once the TOC scrolls out of view (IntersectionObserver); shows current section; click = `window.scrollTo` with measured nav offset (+24px), focus after 420ms; hidden ≤480px / on print |
| **Article end-matter** | non-ADR articles | `.article-end-matter`: accent rule + "Ascendion Engineering Knowledge Base" tag + `← [Section]` hub link. **No dark box.** |
| **ADR colophon** | ADR articles | `.adr-colophon`: "End of Document" stamp + 4-column governance grid (Maintained by / Review Cadence / Change Requests / Version History) |
| **Anti-pattern flip cards** | pages with Anti-Patterns | `.antipattern-card`; back face **light** (`--bg-subtle`), terracotta left border — never a dark fill |
| **Principle flip cards** | "Six principles" section | 6 numbered cards |
| **Footer** | every page | dark, click = scroll to top |

---

## 7. SEO & analytics (head standards)

- Per-page `<head>` (via `build_seo_head`): `<title>` ≤60 displayed chars,
  meta description ≤160, canonical, robots, keywords (base + per-section +
  title), Open Graph (1200×630 image per section under `/assets/og/`),
  Twitter `summary_large_image`, JSON-LD `@graph` (WebSite + Organization +
  TechArticle + BreadcrumbList), theme-color `#0C2240`, preconnect/dns-prefetch.
- Build artifacts: `sitemap.xml`, `feed.xml`, `llms.txt` + `llms-full.txt`
  (AI retrieval), `robots.txt` (allows GPTBot / Google-Extended /
  anthropic-ai / ClaudeBot / PerplexityBot / CCBot / cohere-ai).
- **GA4** `G-W7F7SG5F83`: base tag every page, `send_page_view: false`, ONE
  manual `page_view` with `content_group`; article event tracking
  (scroll_depth, reading_time, toc_click, float_toc_click, diagram_viewed,
  reference_click, antipattern_flip).

---

## 8. Responsive & accessibility

- Breakpoints in `shared.css`: 900px (colophon 4→2 col), 560px (1 col),
  480px (floating button → icon-only).
- Skip link to `#main` on every page.
- WCAG 2.2 AA target; 48×48 / 44×44 touch targets; focus-visible outlines
  in accent; `aria-label`s on nav/TOC/button/end-matter.

---

## 9. Known drift / cleanup backlog

1. **Diagram init is duplicated** in every `diagram.mmd` instead of injected
   from one constant. Centralize as a single `MMD_INIT` the generator prepends.
2. **`MERMAID_INIT`** (generate.py ~line 2169) is the *old* per-page-diagram
   theme and differs from the standardized init above — reconcile.
3. Two `.diagram-wrap` rules exist in `shared.css` (≈330 and ≈2325) — dedupe.
4. CLAUDE.md still says "18-section taxonomy" / "73 substantive pages" — the
   repo now has ~31 sections and 182 article pages. Update.

---

*Maintained by the Solutions Architecture practice. Change values here AND in
`src/shared.css` / `tools/generate.py`; rebuild with
`python tools/generate.py --clean` and verify against the two reference
exemplars.*
