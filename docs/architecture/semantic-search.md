# Semantic search — architecture & operational characteristics

**Scope:** How the in-browser semantic search subsystem works on `ascendion.engineering`.
**Audience:** Solutions architects, senior engineers, FSI security reviewers, and future maintainers.
**Status:** Reference document. Operational metrics in §7 are preliminary pending T7.4b measurements.

---

## 1 — Executive summary

`ascendion.engineering` runs a fully client-side semantic search engine. When a user types a query, the search runs entirely in the user's browser: a 33MB neural network embeds the query into a 384-dimensional vector, that vector is compared against pre-computed embeddings of all content chunks, and the top matches are ranked by similarity. No server-side inference. No query logging. No third-party API calls after first page load.

The architecture trades a one-time download cost (33MB model, ~2MB embeddings) for ongoing operational simplicity, privacy, and zero per-query infrastructure cost. After first visit, all subsequent searches complete in under 100ms with no network activity.

This document explains the components, the data flow, the cache architecture, the security and compliance posture, and the future scaling path.

---

## 2 — The five artifacts that make search work

Search depends on five files. Three are loaded once per browser and persisted in browser storage; two are versioned with the content build.

### 2.1 The four model files (~33 MB total)

All four are fetched from `https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/...` on first use, then cached in the browser's Cache Storage API under the bucket name `transformers-cache`.

| File | Size | Purpose |
|---|---|---|
| `onnx/model_quantized.onnx` | ~34 MB | The neural network itself. BERT-base architecture, 12 transformer layers, 12 attention heads, 384 hidden dimensions, ~33M parameters, int8-quantized for browser use. Computes `f(text) → 384-dim vector`. |
| `config.json` | ~700 B | Architecture metadata. Tells the ONNX runtime how to interpret the `.onnx` file: number of layers, hidden size, vocab size, max sequence length. |
| `tokenizer.json` | ~700 KB | WordPiece vocabulary and subword splitting rules. Maps ~30,000 tokens to integer IDs. Defines special tokens (`[CLS]`, `[SEP]`, `[PAD]`, `[MASK]`, `[UNK]`). |
| `tokenizer_config.json` | ~400 B | Tokenizer behavior: lowercase normalization, max length, tokenizer class. |

The model is `BAAI/bge-small-en-v1.5`, trained by the Beijing Academy of Artificial Intelligence on ~100M sentence pairs using contrastive learning. It is widely deployed in enterprise RAG pipelines and consistently scores in the top tier of the MTEB embedding benchmark relative to its size class. The `Xenova/` namespace is a community-maintained ONNX export of the original PyTorch model, hosted on HuggingFace specifically for browser use via [Transformers.js](https://huggingface.co/docs/transformers.js).

The neural network's job is dimensionality reduction over meaning: arbitrary English text in, fixed-length vector out, with the geometric property that semantically similar inputs produce nearby vectors. Synonyms and paraphrases land in the same neighborhood. This is what makes the search "semantic" rather than "keyword" — typing "audit findings" finds chunks about ISMS observations, compliance gaps, and review reports, regardless of whether the literal phrase appears in the chunk text.

### 2.2 The two content artifacts (~2 MB total)

These are produced by the build pipeline (`tools/build_chunks.py` and `tools/build_vector_index.py`) and served from CloudFront alongside the rendered HTML. They regenerate on every content change.

| File | Size | Purpose |
|---|---|---|
| `chunks.json` | ~1.7 MB | All 724 content chunks across the 73-page library. Each chunk is `{id, page_id, chunk_type, chunk_index, text, references}`. Loaded once into memory as a JavaScript array. |
| `vectors.bin` | ~1.1 MB | Binary array of 724 × 384 float32 embeddings, one row per chunk. Same model used to embed query is used at build time to embed chunks, so query and chunk vectors live in the same 384-dim space. Header: 8 bytes (uint32 count, uint32 dims) + body: count × dims × 4 bytes. All vectors are L2-normalized at write time. |

For the file format and build mechanism, see `tools/build_vector_index.py` and the EPIC-2 sections of `docs/v1.1/playbook.md`.

A third file, `index.bin` (~1.2 MB), is also produced at build time and shipped to CloudFront. It contains an HNSW graph built by Python's `hnswlib`. **It is not consumed by the search frontend in v1.1** — see §8 for the architectural pivot context. It is preserved as a forward-compatibility hedge for the v1.2 backend re-evaluation.

---

## 3 — End-to-end search flow

The flow has three observable phases, distinguished by what is and isn't already cached.

### 3.1 Phase 1 — first-ever visit (cold cache)

```
User opens the knowledge graph page
     │
     ▼  HTTP fetches (~250 KB compressed)
  Browser loads index.html, JS, CSS, graph data
     │
     ▼  User presses '/'
  Modal opens. Two parallel kickoffs fire from openSearchModal:
     │
     ├──► ensureSearchModelLoaded()
     │       │
     │       ▼  Imports @xenova/transformers from esm.sh CDN
     │       ▼  Calls tx.pipeline('feature-extraction', 'Xenova/bge-small-en-v1.5')
     │       ▼  Library fetches 4 files from huggingface.co (~33 MB total)
     │       ▼  Service worker caches all 4 files in Cache Storage
     │       ▼  ONNX runtime initializes the model in WebAssembly memory
     │       ◄─ pipeline ready
     │
     └──► ensureSearchIndexLoaded()
             │
             ▼  Promise.all fetch chunks.json + vectors.bin from CloudFront
             ▼  Parse 8-byte vectors.bin header, validate count + dims
             ▼  Construct Float32Array view over the body, zero-copy
             ◄─ chunks + vectors cached in JS module state
     │
     ▼  Both kickoffs resolve
  Modal transitions to "ready" state
     │
     ▼  User types "audit findings"
  300ms debounce fires (T7.3 input handler)
     │
     ▼  performSearch(queryText)
  embedSearchQuery: tokenize → run BGE in WASM → 384-dim Float32Array
     │  (~30-60ms after first inference; first inference is slower
     │   due to ONNX graph JIT warmup)
     │
     ▼  searchKnn(queryVec, 20)
  Loop: 724 dot products against vectors.bin contents
     │  (~1-5ms; brute-force exact cosine since vectors are L2-normalized)
     │  Sort descending, slice top 20
     │
     ▼  renderSearchResults(top20)
  innerHTML rewrite of <ul id="kg-search-results"> with 20 <li>
     │  (~2-5ms)
     │
     ▼  User clicks a result
  activateSearchResult: closeModal → clearLensSelection →
                        selectNode(pageId) → applySearchHighlight()
     │
     ▼  DOM updates: graph dims with teal edges, side panel opens
```

Total cold time: typically 6–12 seconds, dominated by the 33 MB model download. On a fast desktop with good bandwidth, observed ~3 seconds. On a throttled mobile connection, expect 15+ seconds. The spec budget is <8 seconds on representative 4G.

### 3.2 Phase 2 — subsequent visits in the same browser (warm cache)

The same code paths run, but with cache hits at every fetch boundary:

- The 4 model files: served by the service worker from Cache Storage. Zero network requests.
- The ONNX model bytes: re-loaded into WASM memory from the cached blob. ~50–200ms.
- `chunks.json` and `vectors.bin`: served from the browser's HTTP cache (or revalidated via CloudFront, depending on cache headers — see §4).

Result: the modal opens to "ready" in ~500ms, the first query in the session may have a slight pipeline JIT warmup tax (~50-80ms for the first inference), and every subsequent query completes in ~30-50ms total (embed + kNN + render). Spec budget is <200ms for same-session subsequent searches.

### 3.3 Phase 3 — cached-second-visit first search

The spec defines this scenario specifically: a user comes back the next day, opens the knowledge graph page fresh, presses `/`, and types a query. Phase 1's downloads do not repeat — Cache Storage persists across browser sessions — so this is functionally Phase 2 with cold WASM memory state. Expected total: <500ms. Spec budget is <500ms.

---

## 4 — Cache architecture: two caches, two policies

This is the most subtle part of the architecture and the one most worth understanding. There are two independent caching layers, with two different invalidation models.

### 4.1 Cache 1: the model files (Cache Storage, browser-managed)

Stored under bucket `transformers-cache` in the browser's Cache Storage API. Visible in DevTools → Application → Storage → Cache storage.

**Identity:** keyed by the full URL path. The browser treats `https://huggingface.co/Xenova/bge-small-en-v1.5/resolve/main/onnx/model_quantized.onnx` as a stable, immutable resource.

**Invalidation:** never invalidates while we keep referencing the same model identifier. If we change the model in code (say, upgrade to `bge-large-en-v1.5`), the URL path changes, the new path triggers a fresh download, and the old cached files become orphans that the browser eventually evicts under quota pressure.

**Implication:** adding new pages, new chunks, new content does *not* invalidate the model cache. The model encodes English-language semantics — it has no awareness of which specific knowledge base is using it. Same brain, more knowledge.

**Eviction:** occurs when the user explicitly clears site data, when browser storage quota fills (the model uses ~33 MB of the typical multi-GB origin quota; eviction in practice is rare), or when the service worker's cache strategy explicitly invalidates (we don't do this).

### 4.2 Cache 2: chunks.json and vectors.bin (HTTP cache, server-controlled)

Stored under standard HTTP cache, keyed by URL. CloudFront in front of S3 sets the `Cache-Control` headers that govern freshness.

**Identity:** keyed by URL path. Today both files have stable filenames (`chunks.json`, `vectors.bin`).

**Invalidation:** on every content build, both files are regenerated with new contents but the same filenames. Cache freshness is therefore controlled entirely by HTTP cache headers:

- `Cache-Control: max-age=N` — browser caches for N seconds before revalidating
- `Cache-Control: no-cache` — browser revalidates on every request (cheap conditional GET)
- `Cache-Control: no-store` — browser must always re-fetch fully (most expensive, rarely justified for static content)

The current header configuration is set by the deploy pipeline and should be inspected via `curl -I https://ascendion.engineering/knowledge-graph/agent/v1/vectors.bin`.

**Recommended invalidation strategy (logged as F13 deferred):** content-addressed filenames at build time. Generate `vectors.<sha256>.bin` and reference the hashed filename in HTML. New content → new hash → new filename → forced fresh fetch, with old filenames cacheable indefinitely. This is the standard approach for static-asset versioning and avoids the freshness-vs-staleness tradeoff entirely.

### 4.3 The mental model

> The model is *content-addressed by model name*. It does not change as our knowledge grows. Same brain, more knowledge.
>
> The vectors are *content-addressed by build version*. They regenerate every time we add a page. The brain re-reads the library each release.

Both caches dramatically reduce cold-start cost. Neither cache leaks user data. Both invalidate predictably along their respective axes.

---

## 5 — Why this architecture

The decision tree behind the architecture as it currently exists.

### 5.1 Why semantic search instead of keyword search

Keyword search (e.g., Lunr.js, FlexSearch, Elasticsearch text queries) requires the user to know the vocabulary of the corpus. A user typing "audit findings" gets no hit on a chunk titled "ISMS effectiveness measurements" even though they describe the same concept.

Semantic search via embeddings collapses synonyms, paraphrases, and conceptually-related phrasings into nearby points in vector space. The top hit for "audit findings" was a chunk about ISMS effectiveness measurements — exactly the right behavior for an architecture knowledge library where the same concept appears under multiple framings.

The cost is the embedding model — ~33 MB and a few seconds of cold-start. The benefit is significantly better recall on conceptual queries, especially from users who don't yet know the library's preferred terminology.

### 5.2 Why client-side instead of server-side

A server-side search architecture would replace the browser's BGE inference with an HTTP call to an embedding API (OpenAI, Cohere, self-hosted SentenceTransformers, etc). Compared to that:

**Client-side wins:**
- Zero per-query infrastructure cost. After CDN delivery of static files, search is free.
- No query logging. The user's query never leaves the browser.
- No third-party API dependency. Works after first visit even if HuggingFace is down.
- No rate limits, no API key management, no latency from backend round trips.
- Trivially horizontally scalable — every user runs their own search engine.

**Client-side costs:**
- One-time 33 MB download per user. Significant on slow connections.
- Browser memory footprint during search session (~150 MB peak observed).
- Performance varies by user device. A low-end Android may take 30+ seconds to first-paint search.

For a knowledge library expected to serve a few hundred to a few thousand professional users on capable hardware, the client-side trade-off is unambiguously better. For a public-facing site with millions of users on heterogeneous devices, server-side starts to win on aggregate UX consistency.

### 5.3 Why brute-force kNN instead of HNSW

The original v1.1 spec called for HNSW (Hierarchical Navigable Small World), a graph-based approximate nearest-neighbor algorithm. HNSW is the standard for million-scale vector search; at our scale (724 vectors), it is overkill.

During T7.2 implementation, integrating `hnswlib-wasm` revealed a structural mismatch: the library is designed for a browser-builds-index data flow (in-WASM `addItems()` followed by IDBFS persistence), not the server-builds-index data flow we use (Python `save_index()` → fetch as ArrayBuffer → consume in browser). The library has no public byte-injection API for loading a pre-built index from a fetched buffer.

After confirming this with library author docs and three diagnostic integration attempts, the architecture pivoted to **Option A: brute-force exact cosine kNN in pure JavaScript**. For 724 vectors × 384 dims, this is ~278K float multiply-adds per query — empirically 1–5 ms on commodity hardware. HNSW's algorithmic advantage materializes around 5,000–10,000 vectors. We are 7–14× below that threshold.

The architectural pivot is documented in the T7.2 commit message and the EPIC-7 retrospective. Re-evaluation deferred follow-up F8 governs when to revisit (likely candidates: `voy`, `usearch`, both designed for cross-language buffer-based serialization).

### 5.4 Why this specific embedding model

`BAAI/bge-small-en-v1.5` was chosen over alternatives (MiniLM, e5-small, GTE-small) for the combination of:

- **Quality on technical text** — trained on a corpus that includes scientific papers and code documentation, performs well on retrieval tasks involving technical terminology.
- **Size** — 33 MB quantized is at the upper edge of acceptable for a one-time browser download. Larger models (BGE-base, BGE-large) deliver marginal quality gains at 4× the bandwidth cost.
- **Browser availability** — the Xenova ONNX port is mature, well-maintained, and integrates cleanly with Transformers.js.
- **Open license** — MIT, no commercial usage restrictions.

The model is committed to as a v1.x architecture decision. Migrating to a different embedding model requires re-embedding the entire chunk corpus on the Python build side, since query and chunk vectors must come from the same model.

---

## 6 — Security and compliance

This section is structured for FSI security review consumption.

### 6.1 What is and isn't stored

The browser caches public, open-source model weights. The cache contains:

- **Model weights** (`model_quantized.onnx`) — published by Beijing Academy of AI under MIT license; exact equivalents downloadable directly from HuggingFace
- **Tokenizer vocabulary** (`tokenizer.json`) — derived from BERT's pre-training corpus; non-personal
- **Configuration files** (`config.json`, `tokenizer_config.json`) — small JSON metadata

The cache does **not** contain:

- Search queries (queries are processed in-memory only and never persisted)
- User identifiers, session state, or authentication tokens
- Any personally identifiable information
- Knowledge graph content (`chunks.json` and `vectors.bin` are in the HTTP cache, not Cache Storage, but also contain no PII — they are derived from the public ascendion.engineering content corpus)

### 6.2 Privacy posture

Search queries are processed entirely in the browser. The query text never leaves the user's device. No analytics endpoint, no telemetry, no cookie-based session tracking is performed by the search subsystem. The user's intent (what they searched for, what they clicked) is observable only by the user's own browser DevTools.

Data subject under Philippines RA 10173 (Data Privacy Act) or GDPR Art. 6: no personal data is collected, stored, or transmitted by the search subsystem. No consent banner specific to search is required, though if the parent site has a cookie/consent banner, search activation could be gated for explicit user awareness.

### 6.3 Supply chain integrity

The four model files are fetched from `huggingface.co` on first visit. Risk vectors:

- **DNS hijack / MITM:** mitigated by HTTPS with HSTS. Defeating this requires compromising the user's certificate store.
- **CDN compromise:** unmitigated by the architecture. A compromised HuggingFace CDN could serve a malicious model that returns biased embeddings or, in an extreme case, a crafted ONNX file containing exploits against the WASM runtime.
- **Same-origin policy:** cached files are accessible only to JavaScript loaded from the same origin (`ascendion.engineering` in production). Cross-origin scripts cannot read or tamper with the cache.

### 6.4 Identified gaps and recommended mitigations

**SRI (Subresource Integrity) is not currently enforced on the model files.** Best practice for static dependencies is to pin the SHA-256 of each file in the HTML and have the browser refuse to load if the hash mismatches. This closes the CDN-compromise vector entirely. **Logged as F12 deferred follow-up; recommended for v1.2.**

**Model self-hosting is not currently configured.** For strict-network FSI deployments (e.g., a bank's intranet where outbound connections to huggingface.co are blocked), the model files would need to be mirrored to ascendion-controlled CloudFront with `tx.env.remoteHost` reconfigured. ~33 MB of static files; trivial to mirror. **Logged as F12 deferred; required for any deployment behind enterprise outbound-filtering.**

### 6.5 Third-party component review

For ISO 27001 / SOC 2 audit purposes, the search subsystem introduces these third-party dependencies:

| Component | Source | License | Risk profile |
|---|---|---|---|
| `@xenova/transformers` | npm / esm.sh | Apache-2.0 | Actively maintained; widely adopted; no current CVEs |
| `bge-small-en-v1.5` model weights | HuggingFace `Xenova/` namespace | MIT | Static artifact, immutable once cached |
| `onnxruntime-web` (transitive) | bundled with Transformers.js | MIT | Microsoft-maintained; mature |

No runtime code is fetched from third parties after first page load. All third-party JavaScript is fetched once via `https://esm.sh/@xenova/transformers@2.17.2` (pinned version) and cached.

### 6.6 Data residency

After first load, all search infrastructure runs locally and on infrastructure under our AWS account in `ap-southeast-2`. Once the model is cached, no cross-border data flow occurs from the search subsystem. The first-load fetch from `huggingface.co` is the only cross-border touchpoint, addressable via §6.4 self-hosting if required by deployment context.

---

## 7 — Operational characteristics

> **Note on data freshness:** the metrics below are preliminary, derived from a single Tier 1 cold session captured during T7.4a smoke-testing. The full T7.4b measurement protocol (5 cold + 5 warm runs per tier across 2 device tiers, plus payload size verification) will replace this section. Updated: pending.

### 7.1 Tier 1 — modern desktop, no throttling

Single observed cold session:

| Phase | ms | Notes |
|---|---|---|
| `vector_load` | 370.8 | 1,112,072 bytes, 724 chunks, 384 dims, served over localhost |
| `model_load` | 5,690.8 | First-time download + ONNX initialization (variability observed: 2,289 ms on a separate run) |
| `embed_query` (warm) | 20.3–32.1 | Steady-state after first inference; first inference observed at 59.7 ms (pipeline JIT warmup) |
| `knn_search` (warm) | 0.5–1.3 | Sub-millisecond brute force over 724 vectors |
| `render_results` (warm) | 1.5–3.3 | innerHTML rewrite of 20 result items |

Steady-state warm query: ~25–35ms total (embed + kNN + render). Well within the <200ms spec budget for same-session subsequent searches.

### 7.2 Tier 3 — DevTools-throttled (4× CPU + Slow 4G)

To be measured. Spec budget: first-search-after-fresh-load <8s on representative 4G.

### 7.3 Cached-second-visit

To be measured. Spec budget: <500ms.

### 7.4 Payload size

Total `dist/knowledge-graph/agent/v1/` payload to be verified against the §5.4 spec budget of <2 MB. The HNSW `index.bin` file (~1.2 MB), still produced by the build pipeline despite not being consumed at runtime, may push the on-disk total over budget while the over-the-wire size remains in budget. Decision pending T7.4b data.

### 7.5 Known transient warnings

The browser console emits two warnings during model load:

```
module "buffer" not found
module "long" not found
```

These originate from `onnxruntime-web` checking for optional Node.js modules in a browser context. They do not affect Transformers.js operation and can be suppressed at the `tx.env` configuration level if desired. Documented here for transparency.

---

## 8 — Future scaling and migration paths

### 8.1 At ~5,000 chunks (estimated 4–5× content growth)

Brute-force kNN crosses into uncomfortable territory. ~278K multiply-adds per query becomes ~1.4M; observed latency moves from ~5 ms to ~25 ms. Still within budget but no longer free.

Recommended action: re-evaluate the search backend. Candidates include:

- **`voy`** — Rust/WASM HNSW library designed with cross-language buffer serialization as a first-class concern. Accepts pre-built indices from buffers without IDBFS roundtrip.
- **`usearch`** — Modern ANN library with multi-language support, including a clean WASM build and standard ABI for serialized indices.

The HNSW `index.bin` file produced by the current build pipeline is preserved specifically for this migration. **Logged as F8 deferred follow-up.**

### 8.2 At ~20,000+ chunks

Browser memory pressure becomes a concern; a 20,000-vector × 384-dim Float32Array is ~30 MB resident, on top of the model's WASM heap. At this scale, server-side embedding starts to dominate the cost model. Migration likely involves splitting embedding (still client-side) from vector search (now server-side via a vector database like Qdrant, Weaviate, or pgvector).

### 8.3 Multi-tenant or strict-network deployment

Two decisions to make ahead of any FSI deployment:

1. **Self-host model files.** Mirror the four files to ascendion-controlled CloudFront, configure `tx.env.remoteHost`. F12.
2. **Add SRI hashes** for the cached files. F12.

### 8.4 Quality improvements (no scaling pressure)

- **Re-ranking via cross-encoder** for top-N results. ~10× more expensive per result but significantly better precision. Worth it if user feedback indicates relevance gaps.
- **Query expansion** via small LLM. Not feasible client-side at v1.x architecture.
- **Hybrid search** (BM25 + dense): catches exact-phrase queries that semantic search may rank poorly. Lunr.js + BGE in parallel, score fusion at the top.

---

## 9 — References

### Internal documents
- `docs/v1.1/spec.md` — original architectural specification
- `docs/v1.1/playbook.md` — implementation playbook with EPIC-by-EPIC narratives
- `docs/v1.1/epic-7-decisions/README.md` — locked decisions for the search EPIC
- Commits `c6d83aa` (T7.1), `12a1ba0` (T7.2), `7481787` (T7.3), `a124595` (T7.4a)

### External
- [BGE: Making Text Embeddings by Packaging Diverse Tasks](https://arxiv.org/abs/2309.07597) — Xiao et al. 2023, the BGE paper
- [Transformers.js documentation](https://huggingface.co/docs/transformers.js) — Joshua Lochner / HuggingFace
- [ONNX Runtime Web](https://onnxruntime.ai/docs/get-started/with-javascript.html) — Microsoft
- [HNSW: Efficient and robust approximate nearest neighbor search](https://arxiv.org/abs/1603.09320) — Malkov & Yashunin 2016

### Deferred follow-ups referenced in this document
- **F8** — Re-evaluate vector search backend at 5K-chunk threshold (voy, usearch)
- **F12** — Model self-hosting + SRI for FSI / strict-network deployments
- **F13** — Content-addressed filenames for `vectors.bin` and `chunks.json`

All deferred items are tracked in the EPIC-7 retrospective.
