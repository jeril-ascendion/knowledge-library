# EPIC-7 — Semantic search — retrospective

**Companion to:** `README.md` (locked decisions made before implementation)
**Written:** at EPIC-7 close, after T7.4b shipped (commit `781bba1`)
**Author:** Drafted for Jeril John Panicker, Platform Engineering, Ascendion
**Pattern note:** First EPIC retrospective in v1.1. EPICs 5 and 6 closed without retros; this document establishes the discipline going forward and is intended to be matched in EPIC-8 onward.

---

## 1 — What shipped

Six commits on `feature/kg-v1.1/semantic-search`:

| Commit | Subject | Lines |
|---|---|---|
| `c0f875a` | docs(kg): lock EPIC-7 architectural decisions before T7.1 | +216 |
| `c6d83aa` | feat(kg): integrate Transformers.js with search modal foundation (T7.1) | ~+200 |
| `12a1ba0` | feat(kg): semantic search backend with brute-force cosine kNN (T7.2) | +208/-1 |
| `7481787` | feat(kg): wire search results into modal UI with debounce + click-to-open (T7.3) | +442/-3 |
| `a124595` | feat(kg): add ?perf=1 instrumentation for six-phase timing capture (T7.4a) | +69 |
| `e907266` | docs(architecture): add semantic-search system explainer | +376 |
| `781bba1` | docs(perf): T7.4b — performance characterization for v1.1 search subsystem | +239/-15 |

User-facing deliverable: a fully working in-browser semantic search at the knowledge graph, with a `/`-triggered modal, debounced live results, combobox keyboard navigation, click-to-open with graph dimming, and zero server-side dependencies after first load.

Engineering deliverables: 12 locked architectural decisions, six-phase performance instrumentation, a 3,500-word system explainer, a 2,000-word performance characterization, and a registry of seven deferred follow-up items for v1.2 spec input.

## 2 — What changed from the spec

### 2.1 The Option A architectural pivot

The original v1.1 spec called for HNSW-based approximate nearest-neighbor search via `hnswlib-wasm`. The implementation pivoted mid-EPIC to brute-force exact cosine kNN in pure JavaScript over a Float32Array view of `vectors.bin`. Discovery of the architectural mismatch and subsequent pivot consumed roughly 8 hours of investigation across one session. Three integration attempts surfaced three distinct issues in sequence:

1. The jsDelivr `+esm` CDN transform broke `onnxruntime-web`'s WASM backend registration — resolved by switching to `esm.sh`.
2. `hnswlib.FS` was not exposed on the runtime instance in 0.7.0 — the FS handle is hidden from the public API.
3. `EmscriptenFileSystemManager` is exposed on the loaded instance but offers no documented byte-injection method for loading a Python-built index from a fetched ArrayBuffer.

The root cause turned out to be architectural, not API-surface: `hnswlib-wasm` 0.7.0's data flow assumes browser-builds-index (in-WASM `addItems()` followed by IDBFS persistence). Our pipeline is server-builds-index (Python `save_index()` → fetch as ArrayBuffer → consume in browser). The library was never designed for our model.

The pivot to brute-force kNN was both technically sound and quantitatively justified: at 724 vectors × 384 dimensions, brute-force completes in <1 ms after warmup — empirically faster than the HNSW path would have been at this scale, with no observable accuracy or latency cost. HNSW's algorithmic advantage materializes around 5,000–10,000 vectors. We are 7–14× below that threshold.

### 2.2 What this means for the existing artifacts

The `index.bin` HNSW graph file is still produced by `tools/build_vector_index.py` at every build. It is not consumed by the search frontend. It is preserved as a forward-compat hedge: when the corpus crosses the 5K threshold, F8 (vector search backend re-evaluation) becomes the trigger to either resume consuming `index.bin` or migrate to a different ANN library that better fits server-builds-index data flow (`voy`, `usearch`).

### 2.3 What didn't change

All 12 architectural decisions locked before implementation held. The modal UI, lens-vs-search layering, keyboard navigation patterns, debounce timing, and graph state classes shipped exactly as specified. The pivot was confined to a single structural decision (search algorithm) without cascading changes to the rest of the design.

## 3 — What we learned

### 3.1 The CDN-for-WASM-libraries lesson

`jsDelivr/+esm` performs an aggressive transform on imported modules to convert them to ES module format. For libraries that ship raw WASM and JavaScript glue (Transformers.js, hnswlib-wasm, anything `onnxruntime-web`-based), this transform breaks runtime registration of the WASM backend. The library loads but cannot execute.

`esm.sh` preserves the bundle structure and works correctly for these libraries. This pattern is now established and documented; future WASM-bundled library imports should default to `esm.sh`.

### 3.2 The library-API-fit lesson

When integrating a third-party library that ships pre-built artifacts at server side and consumes them at client side, **library data-flow assumptions matter more than benchmark numbers**. We chose `hnswlib-wasm` for its scaling characteristics (great at millions of vectors) without sufficient diligence on how it expected to be loaded. The library's intended use case (RAG-in-the-browser with embeddings built incrementally and persisted to IDBFS) is structurally different from ours.

The cost of this lesson was 8 hours of investigation. The mitigation going forward: library evaluation should include an explicit "does this library's data-flow shape match ours?" diligence step before benchmark-based selection. For v1.2, this means evaluating `voy` and `usearch` specifically against the server-builds-index → fetch-buffer → consume pattern, not just against query-time benchmarks.

### 3.3 Diagnostic discipline that worked

Several patterns held under pressure across the multi-day debugging arc:

**Pre-flight introspection before action.** Every patch applied to `tools/generate.py` was preceded by `grep`/`sed` to confirm exact line ranges and surrounding bytes. This caught one near-miss where a blank-line whitespace difference would have broken a `str_replace` precondition.

**Lock decisions before implementation.** The `epic-7-decisions/README.md` document was committed before T7.1 began. When implementation hit ambiguity (e.g., should result-click clear lens entirely or just visually override?) the locked-decision pattern resolved the question without re-opening the spec.

**Transactional Python patches with precheck.** Every multi-anchor patch script ran a precheck loop that verified each `old_block` matched exactly once before any write. When preconditions failed (e.g., the `__searchIndex` regression patch where 2 of the original 8 anchors had moved), the script aborted cleanly without partial state. This is now the established pattern for any patch touching multiple anchors.

**Read the actual error before patching.** During the T7.3 regression that surfaced in browser testing (`Uncaught ReferenceError: __searchIndex is not defined`), the diagnostic discipline of reading the Console error rather than guessing routed us directly to the two stale references in `openSearchModal()`. Cost: ~3 minutes diagnosis, ~5 minutes patch. Without this discipline, debugging-by-bisection on the search subsystem could have consumed hours.

### 3.4 Instrumentation timing — a lesson for next time

Performance instrumentation (T7.4a) was wired *after* T7.3 shipped. This was nominally correct per the playbook (T7.4 is the perf task), but in practice meant the T7.2 architectural decision (brute-force vs HNSW) was made on theoretical grounds rather than measured ones. We were lucky — brute-force at our scale is unambiguously the right call regardless of measurement — but a different architecture decision could have benefited from earlier instrumentation.

For v1.2 and onward: wire perf instrumentation early, even before the architecture is finalized. The `?perf=1` machinery can be in place at first commit of the EPIC and produce data that informs subsequent decisions. Cost: ~30 minutes of additional plumbing at EPIC start.

## 4 — Deferred items (the F-registry)

Seven items deferred to v1.2 or later, identified during EPIC-7 work and documented in their respective commits and architecture docs:

| ID | Description | Trigger | Rough effort | Target |
|---|---|---|---|---|
| F2 | Real-device Tier 2/3 validation (Pixel 6, Galaxy A 4 GB) | Pre-GA gate before public launch | ~4 hours (2 devices, full protocol per device) | v1.1 GA |
| F8 | Vector search backend re-eval (voy / usearch) | Corpus reaches ~5,000 chunks | 1–2 days for evaluation + integration | v1.2 if growth is fast; v1.3 otherwise |
| F10 | Render chunk anchors in page panels for in-page scroll-to-chunk | UX feedback that result-click should jump to exact paragraph | ~4 hours; touches `gen_article()` and `build_chunks.py` | v1.2 candidate |
| F11 | Search modal UX polish (depth, micro-interactions, search-icon prefix, no-results visual treatment) | Aesthetic feedback from client demos | ~2 hours per polish iteration | v1.2 candidate |
| F12 | Self-host model files + SRI hashes | FSI deployment behind strict-network filtering | ~30 min implementation; ~33 MB CloudFront mirror | v1.2 candidate; required for FSI |
| F13 | Content-addressed filenames (vectors.&lt;sha256&gt;.bin) | Content update cadence accelerates beyond manual cache-bust comfort | ~1 hour | v1.2 candidate |
| F14 | Smaller embedding model option (MiniLM-L6, 25 MB vs 33 MB) | Mobile usage proves dominant; cold-load p95 needs reduction | ~2 hours including re-validation | v1.2 candidate |

This registry is the v1.2 spec input. All items are scoped, bounded, and evidence-based — none are speculative.

## 5 — Decision 10 budget edge

The cold-load p95 measurement landed at the 8 s spec budget on Tier 1. This was anticipated by Decision 10 ("If p95 budget violated on low-end Android: file an issue, document mitigation, do NOT block EPIC ship") but the boundary case is worth recording explicitly:

- **Tier 1 p95 ≈ 8 s** on direct broadband, dominated by HuggingFace CDN fetch variance for the 33 MB model
- **Tier 1 median ≈ 5.7 s** — comfortably within budget
- **Tier 3 will exceed budget significantly** by simple physics (33 MB at Slow 4G's 1.5 Mbps = ~22 s of network alone)

The cold-load budget edge applies to first-ever browser visits. Cached-second-visit (the dominant access pattern for repeat users) projects to ~200 ms — well within the 500 ms budget. Same-session repeat queries pass by ~4×.

The mitigation path is documented: F12 (self-host model files, ~3× variance reduction by serving from CloudFront ap-southeast-2 edge instead of HuggingFace CDN) is the highest-leverage single change. F14 (smaller MiniLM model, ~25% size reduction) is the second. Both target v1.2.

## 6 — Process observations

### 6.1 Decision-locking before implementation

EPIC-7 followed the EPIC-5/EPIC-6 pattern of writing locked decisions before any code. Twelve decisions captured in `epic-7-decisions/README.md`. All twelve held through implementation. When implementation hit ambiguity, the locked-decision document resolved it. Recommendation: continue this pattern for all future EPICs.

### 6.2 Multi-session work with carryover context

EPIC-7 spanned multiple working sessions over ~3 days, including two WSL crashes and one full-context-window summarization. The disciplines that preserved context across sessions:

- **Commit small and often.** Each task (T7.1, T7.2, T7.3, T7.4a, T7.4b, plus the architecture doc) shipped as its own commit. After every WSL crash, `git log --oneline` immediately re-established where we were.
- **Decision documents, not just code.** The `epic-7-decisions/README.md` doc captured intent in human-readable form. After session breaks, re-reading the locked decisions was sufficient context recovery for resuming implementation.
- **`.bak` safety nets.** During T7.2's diagnostic chaos, `tools/generate.py.bak.t72` was created as a known-good restore point. It was never used (transactional patches held) but the safety it provided enabled willingness to attempt risky changes.

### 6.3 Heredoc fragility in long-form writing

A repeating friction point was bash heredocs for commit messages and patch scripts. Long heredocs pasted into a fast terminal occasionally truncated mid-content (the T7.4b commit message lost its mitigation section to truncation; the cause was paste speed, not the heredoc itself). For future EPICs, prefer:

- **Write the file separately** (`cat > /tmp/patch.py` heredoc, then `python3 /tmp/patch.py`) rather than inline `python3 <<'PYEOF' ... PYEOF` for any non-trivial script
- **Shorter commit messages** (5–10 lines) with the full story in the doc that the commit references
- **Verify file size after writing** (`wc -l /tmp/file`) before running it

### 6.4 The aesthetic-vs-functional moment

At T7.3 acceptance review, a moment occurred where comparison reference modals (AppCo, Hotwire, dark-themed) prompted reconsideration of the just-shipped modal's polish. The decision to ship working code now and log F11 for v1.2 polish was correct — re-opening Decision 1 (modal layout) at end of a long debugging session would have produced regret-worthy aesthetic decisions. Recommendation: aesthetic polish is its own kind of work, distinct from functional implementation, and benefits from being scheduled separately rather than inserted opportunistically.

## 7 — Recommendations for v1.2

Direct inputs to the v1.2 specification, derived from EPIC-7 work:

### 7.1 Architectural

- **Decide on search backend** before implementation: stay with brute-force at current scale, or migrate to `voy`/`usearch` (F8). This is a one-day evaluation, not a multi-day implementation. Do the eval first, lock the decision, then implement.
- **Decide on model hosting** before implementation: continue HuggingFace CDN, or self-host (F12). Self-hosting is required for FSI clients with outbound filtering; if v1.2 includes any FSI deployment target, self-hosting moves from "deferred" to "required."
- **Decide on cache invalidation strategy** before implementation: continue HTTP cache-headers, or move to content-addressed filenames (F13). Content-addressed is the better long-term answer; v1.2 is the right time to make the change before content cadence accelerates.

### 7.2 Process

- **Continue decision-locking before implementation.** Established pattern, demonstrably effective.
- **Wire performance instrumentation at EPIC start, not at perf task.** Cost: ~30 min. Benefit: architecture decisions can be made on measured rather than theoretical grounds.
- **Keep the `.bak` safety-net pattern** during diagnostic chaos. Cost: trivial. Benefit: safety enables willingness to attempt risky patches.
- **Pre-flight introspection (`grep`/`sed`/`view`) before any patch applied to `tools/generate.py`.** Catches off-by-one and whitespace surprises before they corrupt files.

### 7.3 Quality

- **Real-device validation pre-GA (F2)** is genuinely required before public launch, not a nice-to-have. Tier 3 cold-load budget violation is real; we don't yet know how badly it manifests on actual mid-range and low-end Android hardware. Schedule this explicitly.
- **The F-registry is the v1.2 backlog input.** F2/F8/F10/F11/F12/F13/F14 are scoped, bounded, evidence-based. Pick which ones land in v1.2 based on FSI deployment urgency and resource availability; the rest move to v1.3.

## 8 — References

### Internal
- `docs/v1.1/epic-7-decisions/README.md` — the 12 locked decisions
- `docs/v1.1/v1.1-performance.md` — perf characterization (T7.4b deliverable)
- `docs/architecture/semantic-search.md` — system explainer
- `docs/v1.1/playbook.md` — implementation playbook with EPIC narratives
- `docs/v1.1/spec.md` — original architectural specification

### Commits in EPIC-7
- `c0f875a` decisions doc · `c6d83aa` T7.1 · `12a1ba0` T7.2 · `7481787` T7.3
- `a124595` T7.4a · `e907266` architecture doc · `781bba1` T7.4b

---

## 9 — Production incident postmortem (added after section 8)

The retrospective above was written at EPIC-7 close, after `c8420a3` shipped to the feature branch and before the EPIC-7 PR (#18) merged to main. A production incident surfaced within hours of the EPIC-7 deploy and resolved within five hours. This section documents the incident honestly because the lessons it produced are more durable than the EPIC-7 work itself.

### 9.1 What happened

EPIC-7 PR #18 squash-merged to main and deployed to `ascendion.engineering` via the standard GitHub Actions workflow. Build succeeded. Deploy succeeded. CloudFront invalidation succeeded. The first production visitor to `/knowledge-graph/` pressed `/`, the search modal opened, and the model load failed with three `403 Forbidden` responses from S3 for `config.json`, `tokenizer.json`, and `tokenizer_config.json` under the path `ascendion.engineering/models/Xenova/bge-small-en-v1.5/...`.

Search was completely broken on first cold visit for every user.

### 9.2 Why it broke

Transformers.js v2.17.2 defaults `allowLocalModels = true` with `localModelPath = '/models/'`. When `allowLocalModels` is true, the library constructs URLs as `${origin}${localModelPath}${modelId}/...` and tries to fetch from the current origin first. Only if that fetch fails does it fall back to `remoteHost`. But the library treats a same-origin 403 as a hard failure rather than as "not local, try remote" — so the fallback never fired. Production was therefore trying to fetch BGE model files from its own S3 bucket, which doesn't host them, returning 403.

The configuration in EPIC-7 set `allowRemoteModels = true` but did not set `remoteHost` and did not set `allowLocalModels = false`. Both were required for fetches to actually go to HuggingFace.

### 9.3 Why it wasn't caught in development

This is the most important lesson. Throughout T7.1, T7.2, T7.3, T7.4a, T7.4b — every local smoke test and every performance characterization run — Cache Storage masked the bug.

The first time the BGE model was fetched during early T7.1 development, the configuration happened to be in a state that successfully routed to `huggingface.co`. Those files were cached in browser Cache Storage under their `huggingface.co` URLs. Every subsequent local test was a cache hit on those URLs. The library never re-resolved the URL construction logic because it never needed to fetch the files again.

Production was the first session anywhere with a clean cache against a production origin. That session surfaced the misconfiguration immediately.

### 9.4 The remediation arc

Three hotfix attempts were required:

**Hotfix #1 (PR #19, merged):** Set `tx.env.remoteHost = 'https://huggingface.co/'`. Necessary but not sufficient. After deploy, the 403s persisted. Diagnosis was based on the assumption that setting `remoteHost` would override the URL construction. The Transformers.js v2.17.2 source was not consulted before patching.

**Hotfix attempt on the same branch (PR #20, closed without merging):** Added `tx.env.allowLocalModels = false` on top of the merged branch. Because PR #19's commit was already on main as a squash-merge, the branch's two-commit history conflicted with main and PR #20 was permanently un-mergeable.

**Hotfix #2 (new branch, separate PR, merged):** Created a fresh branch `hotfix/search-allow-local-models` from current main, applied only the `allowLocalModels = false` change, opened a clean PR, CI passed, squash-merged, deployed. Production smoke test confirmed model fetches now resolve to `huggingface.co/Xenova/...` with 200 status. Search works on cold-cache first visits.

Total time from incident detection to resolution: approximately five hours. Most of that time was deploy cycles (~6-8 minutes each) and the diagnostic loops that bracketed them.

### 9.5 Lessons — pre-deploy gates that would have prevented this

**Cold-cache smoke testing is mandatory before any deploy of code that touches Cache Storage or external resource fetching.** The procedure takes 30 seconds: DevTools → Application → Clear site data → hard reload → exercise the feature. Every EPIC that ships features touching external resources should include this as an explicit gate in the playbook, not as a vague recommendation.

The EPIC-7 playbook already had the perf characterization tier methodology. It should have had a cold-cache validation step too. This is now logged as a v1.2 playbook addition.

### 9.6 Lessons — diagnostic discipline under production pressure

**Read the actual library source before patching third-party library behavior.** Hotfix #1 was diagnosed in roughly fifteen minutes, patched, and deployed. The diagnosis was wrong. Reading the v2.17.2 `env.js` source — a two-minute task — would have produced the correct two-line patch on the first attempt instead of the four hours of diagnostic ping-pong that actually occurred.

Production pressure creates a bias toward "ship the fix fast" that competes against "verify the fix is correct." In this incident, the fast path was wrong, the deploy cycle is expensive (~8 minutes wall-clock), and three incorrect deploys cost more time than a careful read-the-source diagnosis would have.

The discipline is: when a production-broken state pressures you toward speed, slow down for the diagnostic step specifically. The deploy step can move fast safely; the diagnostic step cannot.

### 9.7 Lessons — Git workflow

**After a PR merges, the next change against the same target lives on a NEW branch from current main, not as added commits to the now-merged branch.** Adding commits to the original branch leaves it with history that conflicts with main's squash-merge of itself. PR #20 spent its lifetime in a permanently-conflicting state because of this.

The recovery procedure (create new branch from current main, cherry-pick or re-apply the new change only, push, open fresh PR) is straightforward, but it has to be recognized as the right move rather than discovered through trial and error. Documenting this here so future EPIC closes don't repeat the duplicate-PR confusion.

### 9.8 Lessons — Python f-string escape audits

The corrective hotfix introduced a transient build failure because the comment text contained `${origin}` (intended as literal JS template literal syntax) inside a Python f-string. Python parsed `${origin}` as an f-string interpolation expression and raised `NameError: name 'origin' is not defined`. Caught locally because the build was tested before push.

**Any f-string in `tools/generate.py` that emits JS containing template literals, or shell containing variable expansion, needs explicit `{{` `}}` escape discipline.** The patch script needs to escape literal braces consistently — `${{origin}}` in Python source renders to `${origin}` in the generated HTML.

The local-build-before-push discipline caught this in two minutes. Without it, the corrective hotfix would have been a CI failure and a re-roll.

### 9.9 What this means for v1.2

Three additions to the v1.2 playbook:

1. **Cold-cache smoke test** is a pre-deploy gate for any change touching Cache Storage or external resource fetching. Procedure documented in the playbook with the 30-second protocol.

2. **Third-party library config patches** require reading the library's documented config keys or source before patching. A 5-minute time budget for this is cheaper than any incorrect deploy cycle.

3. **F12 (self-host model files)** moves from "nice-to-have for FSI" to "required for v1.2." Self-hosting from CloudFront ap-southeast-2 eliminates the entire class of "remote host URL construction" bugs because there's no remote host to route to. It also reduces cold-load p95 variance materially. The cost is ~33 MB of additional S3 storage and one extra build step.

### 9.10 What this does not change

EPIC-7 ships. The architectural pivot to brute-force kNN was sound. The performance characterization holds. The F-registry stands. The 12 locked decisions held through implementation. The retrospective sections 1-8 above are accurate as of EPIC-7 close.

This incident was a delivery-discipline gap, not a design gap. The remediation is procedural (pre-deploy gates, diagnostic discipline, Git workflow clarity) rather than architectural.

The honest reading is: **EPIC-7 was technically correct and operationally underprepared.** The fix for that is documented above and lives in the v1.2 playbook from this point forward.

---

*End of section 9 addendum. The retrospective document is complete as of this addition.*
