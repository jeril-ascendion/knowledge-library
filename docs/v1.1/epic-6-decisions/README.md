# EPIC-6: Concept Lens UI — Locked Decisions

Locked before implementation, May 4, 2026. Pattern follows EPIC-5 decision-locking.

These decisions are referenced as "Decision N" in implementation prompts. Once locked, they should not change without explicit re-discussion.

## Decision 1: Lens registry exposed in two places

The `CONCEPT_LENSES` dict in `tools/seed_content.py` remains the single source of truth. Two derived consumers expose it:

1. **Runtime JS (`GRAPH_DATA.lenses`)**: a top-level array on the rendered HTML's GRAPH_DATA object. Each entry: `{id, label, description, members, caption_source}`. Used by the dropdown (T6.1) and the highlight-and-dim engine (T6.2).
2. **Agent JSON (`index.json` top-level `lenses` array)**: same shape, written by `build_index_json.py`. Consistent with EPIC-3's agent-friendliness pattern. Agents can list available lenses without parsing HTML.

Both arrays are byte-identical so a future cross-validation check (lint, CI) is trivial.

## Decision 2: URL hash format

Existing format: `#node=<id>` (EPIC-5).

Extended format supports an optional `lens` parameter:
- `#node=<id>` — node selected, no lens
- `#node=<id>&lens=<lens-id>` — node selected, lens active
- `#lens=<lens-id>` — no node selected, lens active
- `#node=<id>&lens=all` or absent `lens` key — both mean "no lens"
- Empty hash — no node, no lens

Parser parses the two parameters independently. URL writer maintains both. Stale lens IDs (lens that doesn't exist in the registry) are silently ignored without error, same defensive behavior as stale node IDs in EPIC-5.

## Decision 3: Custom dropdown architecture

Button-triggered custom dropdown (per Q1 product call). NOT native `<select>`.

ARIA pattern: `role="combobox"` on the button, `role="listbox"` on the panel, `role="option"` on each item. `aria-expanded` toggles on the button. `aria-activedescendant` tracks keyboard-focused option.

Keyboard support:
- `Tab` — focus to button
- `Enter` / `Space` / `ArrowDown` on closed dropdown — open
- `ArrowUp` / `ArrowDown` on open dropdown — navigate options
- `Enter` on focused option — select and close
- `Escape` on open dropdown — close, restore focus to button
- `Tab` on open dropdown — close, allow normal tab navigation
- `Home` / `End` on open dropdown — first / last option

Click handling:
- Click on button — toggle open/close
- Click on option — select and close
- Click outside dropdown — close

Focus restoration: closing via Escape or selection returns focus to the trigger button.

## Decision 4: Highlight/dim opacity values and transitions

Per Q2 product call, D3-driven (not pure CSS classes). However, the D3 code TOGGLES classes on nodes; CSS handles the actual opacity transitions. This gives both flexibility and clean visual polish.

Opacity values:
- **Lit nodes** (in lens member set): 100% opacity, normal styling
- **Dimmed nodes** (not in lens member set): 25% opacity
- **Edges between two lit nodes**: 90% opacity, terracotta (#C96330), 1.5x normal stroke-width
- **Edges with one lit endpoint**: 30% opacity (per Q3), original color, original stroke-width
- **Edges with no lit endpoints**: 25% opacity, original color

Transition: 350ms ease-in-out. Slightly under the spec's "~400ms" because 350ms tests as more responsive without feeling rushed.

CSS classes (per sub-decision on EPIC-7 layering): `.lens-lit`, `.lens-dimmed` on nodes; `.lens-edge-lit`, `.lens-edge-fade`, `.lens-edge-dimmed` on edges. Distinct from any future `.search-lit` classes from EPIC-7.

When no lens is active, none of these classes are present (nodes and edges render in their default styling).

## Decision 5: Caption banner rendering and placement

Per Q5 product call, banner sits ABOVE `.kg-shell` at full viewport width.

Render strategy: banner element rendered always-present in the HTML at page render time (in `gen_knowledge_graph_page`), with `style="display: none"`. JS toggles `display: block` and updates text content on lens activation.

Placement: inside `main.kg-page > .shell > .article-body`, immediately before `.kg-shell`. Inherits the full-viewport width treatment from EPIC-5's polish.

Styling:
- Italic Plex Serif, 0.95rem, line-height 1.5
- 4px solid terracotta (#C96330) left border
- Background: rgba(201, 99, 48, 0.04) (very light terracotta tint)
- Padding: 0.875rem 1.25rem
- Margin-bottom: 1rem (separates from kg-shell)
- Text color: var(--ink-2)

No layout shift on toggle (reserve no space when hidden — `display: none` is intentional).

## Decision 6: Search/lens interaction (forward-looking)

EPIC-7 will introduce search. When both search and lens are active, the layering is:
- Search highlights override lens dimming
- Order of dominance: search-lit > lens-lit > dimmed
- Clearing search: lens highlights restore
- Clearing lens: search highlights remain

To support this without rework, EPIC-6 uses CSS class names that don't collide with EPIC-7's expected names. EPIC-6 owns: `.lens-lit`, `.lens-dimmed`, `.lens-edge-lit`, `.lens-edge-fade`, `.lens-edge-dimmed`. EPIC-7 will own: `.search-lit`, `.search-dimmed` (or whatever it scopes).

EPIC-6 does NOT implement any search hooks. It just uses semantic class names that will compose cleanly later.

## Out of scope for EPIC-6

- Multiple simultaneous lenses (EPIC-6 supports one active lens at a time)
- Search interaction (EPIC-7)
- Custom lens creation by user (lens registry is build-time, not runtime-editable)
- Per-page-type lens filters (lenses currently target only pages; standards and sections are unaffected by lens activation visually — they remain at default styling)

## Task structure

- **T6.1**: Lens registry exposure (Decision 1) + custom dropdown component (Decision 3) + URL state extension (Decision 2 read path)
- **T6.2**: D3 highlight/dim engine (Decision 4) + lens activation wiring + URL state extension (Decision 2 write path)
- **T6.3**: Caption banner (Decision 5)
- **Polish**: One round expected per EPIC-5 retrospective lesson F4

Total estimated effort: 2.5-3 hours focused work.
