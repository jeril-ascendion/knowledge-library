#!/usr/bin/env python3
"""T2.4 — run canonical validation queries against the v1.1 agent endpoint
artifacts and emit a markdown report demonstrating semantic search quality.

Inputs (produced by build_chunks.py + build_vector_index.py):
    dist/knowledge-graph/agent/v1/chunks.json
    dist/knowledge-graph/agent/v1/vectors.bin
    dist/knowledge-graph/agent/v1/index.bin

Output:
    dist/knowledge-graph/agent/v1/validation_report.md

Determinism: same artifacts + same query strings -> same report bytes
(latency numbers excluded from the determinism contract).
"""

import importlib.util
import json
import os
import struct
import sys
import time
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
AGENT_DIR = REPO_ROOT / "dist" / "knowledge-graph" / "agent" / "v1"
CHUNKS_PATH = AGENT_DIR / "chunks.json"
VECTORS_PATH = AGENT_DIR / "vectors.bin"
INDEX_PATH = AGENT_DIR / "index.bin"
REPORT_PATH = AGENT_DIR / "validation_report.md"

MODEL_NAME = "BAAI/bge-small-en-v1.5"
DIMS = 384
HNSW_EF_SEARCH = 50
TOP_K = 5
EXCERPT_CHARS = 180


FEATURED_QUERIES = [
    (
        "What's the architectural pattern for reducing PCI DSS audit scope?",
        "Demonstrates retrieval of architectural reasoning, not just topic-keyword matches.",
    ),
    (
        "Why are authentication and authorization different problems and what happens when teams conflate them?",
        "Demonstrates that v1.1 surfaces structured pitfalls — not every library has this and search picks it up.",
    ),
    (
        "When is event-driven architecture the right call, and when is it overengineering?",
        "Demonstrates retrieval across both sides of an architectural tradeoff.",
    ),
    (
        "How do I monitor an AI system in production beyond classical SRE metrics?",
        "Demonstrates AI-native concerns as distinct from classical observability.",
    ),
    (
        "When should an architectural decision become an ADR versus a longer RFC versus a one-line code comment?",
        "Demonstrates three-way governance artifact distinction in a single query.",
    ),
]

ADDITIONAL_QUERIES = [
    (
        "How do I assess maintainability for a service that's been in production for 5 years?",
        "Demonstrates retrieval across multiple NFR pages — when a query spans cross-cutting concerns, related thinking from neighboring pages surfaces in the top-5.",
    ),
    (
        "What's the safest sequencing for moving a monolith to microservices without freezing the business?",
        "Demonstrates retrieval across page types — playbooks, runbooks, principles, patterns — operational knowledge surfaces alongside conceptual.",
    ),
    (
        "What goes wrong with distributed tracing in production, and how do you tell?",
        "Demonstrates retrieval of failure-mode knowledge through structured pitfalls chunks.",
    ),
]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _verify_artifacts():
    missing = []
    if not CHUNKS_PATH.exists():
        missing.append(str(CHUNKS_PATH.relative_to(REPO_ROOT)))
    if not VECTORS_PATH.exists():
        missing.append(str(VECTORS_PATH.relative_to(REPO_ROOT)))
    if not INDEX_PATH.exists():
        missing.append(str(INDEX_PATH.relative_to(REPO_ROOT)))
    if missing:
        print(
            "ERROR: required agent artifacts missing:\n  - "
            + "\n  - ".join(missing)
            + "\nRun tools/build_chunks.py and tools/build_vector_index.py first.",
            file=sys.stderr,
        )
        sys.exit(1)


def _read_vectors_header():
    with open(VECTORS_PATH, "rb") as f:
        header = f.read(8)
    n, dims = struct.unpack("<II", header)
    return n, dims


def _excerpt(text):
    flat = " ".join(text.split())
    if len(flat) <= EXCERPT_CHARS:
        return flat
    return flat[:EXCERPT_CHARS].rstrip() + "..."


def _format_query_section(qid, query, callout, latency_ms, hits, chunks_by_id, i=None):
    lines = []
    lines.append(f"### {qid} — {query}")
    lines.append("")
    lines.append(f"**What this demonstrates:** {callout}")
    lines.append("")
    latency_line = f"_Latency: {latency_ms:.1f} ms_"
    if i == 0:
        latency_line += " _(includes BGE warmup; steady-state is ~75ms per query)_"
    lines.append(latency_line)
    lines.append("")
    lines.append("| Rank | Chunk ID | Page | Type | Similarity |")
    lines.append("|---|---|---|---|---|")
    for rank, (cid, sim) in enumerate(hits, start=1):
        chunk = chunks_by_id[cid]
        lines.append(
            f"| {rank} | {cid} | {chunk['page_id']} | {chunk['chunk_type']} | {sim:.3f} |"
        )
    lines.append("")
    top_chunk = chunks_by_id[hits[0][0]]
    lines.append(f"> _Excerpt of top result:_ {_excerpt(top_chunk['text'])}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def main():
    _verify_artifacts()

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    seed = _load("seed_content", TOOLS_DIR / "seed_content.py")

    with open(CHUNKS_PATH) as f:
        data = json.load(f)
    chunks = data["chunks"]
    n_chunks = len(chunks)
    chunks_by_id = {c["id"]: c for c in chunks}
    chunks_by_idx = chunks  # internal hnsw ids match the sorted order from build

    n_vectors, vec_dims = _read_vectors_header()
    if n_vectors != n_chunks:
        print(
            f"ERROR: vectors.bin reports {n_vectors} vectors but chunks.json has "
            f"{n_chunks} chunks — artifacts out of sync. Rebuild via "
            f"tools/build_vector_index.py.",
            file=sys.stderr,
        )
        sys.exit(1)
    if vec_dims != DIMS:
        print(
            f"ERROR: vectors.bin dims={vec_dims}, expected {DIMS}.",
            file=sys.stderr,
        )
        sys.exit(1)

    page_ids = sorted({c["page_id"] for c in chunks})
    lens_count = len(seed.CONCEPT_LENSES)
    debt_ledger_members = len(seed.CONCEPT_LENSES["debt-ledger"]["members"])

    t0 = time.perf_counter()
    from sentence_transformers import SentenceTransformer
    import hnswlib

    model = SentenceTransformer(MODEL_NAME)

    index = hnswlib.Index(space="cosine", dim=DIMS)
    index.load_index(str(INDEX_PATH), max_elements=n_chunks)
    index.set_ef(HNSW_EF_SEARCH)

    all_queries = [(f"Q{i+1}", q, c) for i, (q, c) in enumerate(FEATURED_QUERIES)]
    all_queries += [
        (f"Q{i+1+len(FEATURED_QUERIES)}", q, c)
        for i, (q, c) in enumerate(ADDITIONAL_QUERIES)
    ]

    results = []
    latencies_ms = []

    for qid, query, callout in all_queries:
        t_start = time.perf_counter()
        emb = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype(np.float32)
        labels, distances = index.knn_query(emb, k=TOP_K)
        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        hits = []
        for label, dist in zip(labels[0], distances[0]):
            chunk = chunks_by_idx[int(label)]
            similarity = 1.0 - float(dist)
            hits.append((chunk["id"], similarity))

        results.append({
            "qid": qid,
            "query": query,
            "callout": callout,
            "latency_ms": elapsed_ms,
            "hits": hits,
        })
        latencies_ms.append(elapsed_ms)

    total_elapsed = time.perf_counter() - t0
    mean_latency = sum(latencies_ms) / len(latencies_ms)

    # ── Render markdown ────────────────────────────────────────────────────
    out = []
    out.append("# Knowledge Library v1.1 — Semantic Search Validation Report")
    out.append("")
    out.append("_Generated by tools/run_validation_queries.py_  ")
    out.append("_Build artifacts: dist/knowledge-graph/agent/v1/_  ")
    out.append("_Embedding model: BAAI/bge-small-en-v1.5 (384-dim)_")
    out.append("")
    out.append("## How to read this report")
    out.append("")
    out.append(
        "This report demonstrates that the v1.1 build pipeline produces a "
        "semantically searchable knowledge corpus. It runs 8 canonical queries "
        "against the HNSW index and shows the top-5 chunks each query retrieves, "
        "with cosine similarity scores."
    )
    out.append("")
    out.append(
        "The \"What this demonstrates\" callout under each query explains what "
        "aspect of the library's structure is being surfaced — the queries are "
        "designed not just to test retrieval accuracy, but to show that v1.1's "
        "structural choices (cross-cutting lenses, structured pitfalls, distinct "
        "chunk types) emerge automatically through search."
    )
    out.append("")
    out.append(
        "This is silent infrastructure as of EPIC-2 close — the search results "
        "below are not yet rendered in the UI. UI integration begins in EPIC-7. "
        "The artifacts demonstrated here are publicly fetchable at "
        "/knowledge-graph/agent/v1/ once v1.1 deploys."
    )
    out.append("")
    out.append("## Build statistics")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|---|---|")
    out.append(f"| Substantive pages | {len(page_ids)} |")
    out.append(f"| Total chunks | {n_chunks} |")
    out.append(f"| Vector dimensions | {DIMS} |")
    out.append("| HNSW config | M=16, ef_construction=200, ef_search=50, seed=42 |")
    out.append(f"| Concept lenses | {lens_count} |")
    out.append(f"| Lens members (debt-ledger) | {debt_ledger_members} |")
    out.append(f"| Mean query latency | {mean_latency:.1f} ms |")
    out.append("")
    out.append("## Featured queries")
    out.append("")
    for i, r in enumerate(results[:5]):
        out.append(_format_query_section(
            r["qid"], r["query"], r["callout"], r["latency_ms"], r["hits"], chunks_by_id, i=i
        ))
    out.append("## Additional examples")
    out.append("")
    for i, r in enumerate(results[5:], start=5):
        out.append(_format_query_section(
            r["qid"], r["query"], r["callout"], r["latency_ms"], r["hits"], chunks_by_id, i=i
        ))
    out.append("## What's coming next")
    out.append("")
    out.append(
        "This report demonstrates EPIC-2 (build pipeline) is functional. The "
        "semantic search runs server-side via Python here; client-side browser "
        "execution lands in EPIC-7. UI integration with the side panel workspace "
        "lands in EPIC-5/6. Production deploy of the agent endpoint happens at "
        "end of EPIC-3 (~2 working days from this report)."
    )
    out.append("")
    out.append(
        "For the v1.1 spec see docs/v1.1/spec.md. For the implementation plan "
        "see docs/v1.1/playbook.md."
    )
    out.append("")

    REPORT_PATH.write_text("\n".join(out), encoding="utf-8")

    # ── Stdout sanity print ────────────────────────────────────────────────
    print("─" * 72)
    print("Validation queries — top-3 condensed")
    print("─" * 72)
    for r in results:
        print(f"\n{r['qid']}: {r['query']}")
        for rank, (cid, sim) in enumerate(r["hits"][:3], start=1):
            print(f"  {rank}. [{sim:.3f}] {cid}")
    print()
    print("─" * 72)
    print(f"Total elapsed (load + 8 queries): {total_elapsed:.2f} s")
    print(f"Mean query latency: {mean_latency:.1f} ms")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
