# EPIC-7 — Locked architectural decisions

Locked before T7.1 implementation. References these decisions
in implementation prompts to avoid relitigating mid-build.

## Context

EPIC-7 is the semantic search frontend. Browser-side ML inference
via Transformers.js (BGE-small-en-v1.5, 384-dim embeddings) +
hnswlib-wasm for kNN over 724 chunks across 73 pages.

Infrastructure (chunks.json + vectors.bin + index.bin) shipped in
EPIC-2. This EPIC consumes those artifacts and wires them to a UI.

## Spec recap (from playbook.md)

- T7.1: Integrate Transformers.js — lazy load, IndexedDB cache,
  loading state with progress callback
- T7.2: Integrate hnswlib-wasm — load vector.bin, ef_search=50,
  k=20 results, resolve indices to chunk objects
- T7.3: Wire input → kNN → highlight + panel results — debounce,
  group by page_id, search wins over lens
- T7.4: Performance characterization on 3 reference devices

## Locked decisions

### Decision 1: Modal architecture

Full-screen overlay with centered card.

- Desktop (>= 880px): centered card max-width 720px, max-height 80vh
- Mobile (< 880px): full-screen modal
- Trigger: search icon in toolbar (between legend and lens dropdown)
  AND keyboard shortcut `/` (Vim/GitHub convention)
- Dismiss: Escape, click outside card, X button in card top-right
- Focus restored to trigger on close
- Modal stays open while user types and reviews results
- Modal closes only on explicit dismissal OR result click

### Decision 2: Result rendering pattern (action-driven, not live)

Modal hosts both input AND results. Graph does NOT dim while user
types — only after the user clicks a result.

Flow:
1. User opens modal (icon click or `/` keypress)
2. User types query
3. After 300ms debounce: embed query, kNN search, render snippets
   in modal results list. Graph remains in default state.
4. User clicks a snippet → modal closes, graph dims to search-lit
   state (matching pages bright, others dimmed), page panel opens
   for the clicked snippet's parent page, scrolled to chunk position.
5. To clear search state from graph: reopen modal, clear input, OR
   click somewhere else (graph default behaviour)

Rationale: Live dim during typing produces flicker as results change.
Action-driven dim keeps the visual story clean: user thinks → commits →
graph reflects.

### Decision 3: Loading states

Three-stage progress feedback.

1. Idle: input placeholder "Search the library…"
2. First-query loading (model + vectors download): full-card
   progress bar driven by Transformers.js progress_callback.
   Copy: "Loading semantic search engine (33 MB, one-time)…
   This download is cached for future visits."
3. Subsequent query (model warmed): thin top-of-card indeterminate
   progress strip with 300ms minimum visibility (avoids flicker
   for very fast queries)

Loading is non-cancellable mid-flight, but Escape always dismisses
the modal (download continues in background, user can reopen).

### Decision 4: Error states

Three distinct error modes with specific copy:

- **Offline / fetch failed**: "Cannot reach search engine. Check
  your connection and try again." + Retry button
- **WASM init failed**: "Search is unavailable in this browser.
  Try a recent Chrome, Firefox, or Safari version." (no retry)
- **Model 404 / hash mismatch**: "Search engine could not load.
  Please try refreshing the page." + Reload button

All errors logged to console with full context. No telemetry in
EPIC-7 (deferred to v1.2 if needed).

### Decision 5: Search ↔ lens layering (search wins)

CSS class names — distinct from EPIC-6's `.lens-*` namespace
per Decision 6 of EPIC-6:

- `.search-lit` — node is in top-N search results
- `.search-dimmed` — node is not in top-N, search active
- `.search-edge-lit` — edge between two search-lit nodes
- `.search-edge-dimmed` — edge with at least one search-dimmed endpoint

Layering rules (CSS specificity):

- `.search-lit` present → render search-lit styling (ignore lens)
- `.search-dimmed` present → render search-dimmed styling (ignore lens)
- No search class → lens classes apply normally
- Search and lens are never both visually active

JS implementation: `applySearch(searchResultPageIds | null)` toggles
`.search-*` classes. When called with null, classes clear and lens
re-applies.

Hashchange listener sequence: clear search → apply lens → render
node selection.

### Decision 6: Search visual styling — distinct cool counterpoint

Search uses a desaturated cool colour to differentiate from the
warm terracotta of lens. Semantic mapping: cool = exploration
(search), warm = domain pattern (lens).

Search-specific values:
- Search-lit nodes: 100% opacity, no fill change (default node
  colours preserved — searching reveals existing colour vocabulary)
- Search-dimmed nodes: opacity 0.20 (slightly more aggressive than
  lens-dimmed 0.25 — search is more focused than lens)
- Search-edge-lit: stroke `#3D7B8C` (desaturated teal),
  stroke-width 3px (vs lens-edge-lit 2.25px), opacity 1.0
- Search-edge-dimmed: opacity 0.20

Transition: 250ms ease-in-out (slightly faster than lens 350ms —
search is action-response, lens is mode-toggle)

### Decision 7: Mobile modal

Same logical component, responsive layout via CSS:

- < 880px: modal occupies full viewport
- Search input pinned to top, results scroll below
- Touch targets minimum 44pt (iOS HIG, Material both agree)
- Input has autocomplete=off autocapitalize=off autocorrect=off
- Virtual keyboard scroll-into-view handled

### Decision 8: Debounce + cancellation

- 300ms debounce on keystroke (per spec T7.3)
- Empty input clears immediately, no debounce
- AbortController on embedding generation: if user types again
  before previous embedding completes, abandon previous, start new
- kNN search itself is fast (~50ms), no cancellation needed there

### Decision 9: Result keyboard navigation (combobox pattern)

Same level of polish as EPIC-6 dropdown.

- Type in input → results render → focus stays in input
- Down arrow from input → focus first result
- Up/Down between results
- Enter on result → activate (close modal, open page, scroll to chunk)
- Escape → close modal, focus restored to trigger
- Up arrow when first result focused → focus returns to input

ARIA pattern:
- Input: `role="combobox" aria-expanded aria-controls aria-activedescendant`
- Results list: `role="listbox"`
- Each result: `role="option" aria-selected`

### Decision 10: Performance budget enforcement

T7.4 outputs `docs/v1.1-performance.md` (new file).

Mode: hidden `?perf=1` URL parameter enables console timing for:
model_load, vector_load, index_load, embed_query, knn_search,
render_results.

Spec budgets:
- First-search-after-fresh-load: < 8s on representative 4G
- Same-session subsequent search: < 200ms
- Cached-second-visit first search: < 500ms

Devices: dev laptop, mid-range Android (Pixel 6 / Galaxy A series),
low-end Android (4 GB RAM).

If p95 budget violated on low-end Android: file an issue, document
mitigation, do NOT block EPIC ship. v1.2 quantization is fallback.

### Decision 11: Modal-as-component (DOM state)

Modal element rendered into HTML at page load with `display: none`.
Toggling `display: flex` on open. NOT created/destroyed dynamically.

Reasoning: Avoids DOM thrash, makes ARIA labels stable across renders,
keeps Transformers.js model state alive between modal opens (model
loads on first open and stays loaded until page reload).

### Decision 12: Schema access pattern (for code clarity)

`chunks.json` top-level shape: `{schema_version: "1.0", chunks: [...]}`.
Access pattern in JS:

```js
const chunksData = await response.json();
const chunks = chunksData.chunks;     // array of 724
const chunk = chunks[i];              // index aligned with vectors[i]
```

Each chunk has: `id, page_id, chunk_type, chunk_index, text,
text_length, references`.

For panel rendering: use `text` for snippet body, derive page title
from `GRAPH_DATA.nodes.find(n => n.id === chunk.page_id).label`.

For "scroll to chunk position" (T7.3 click behaviour):
chunk-type+chunk-index → CSS selector for the section heading on
the page (TBD: requires checking how generate.py renders sections;
deferred to T7.3 implementation but anchor naming should follow a
predictable pattern like `#chunk-{chunk_id}`).

