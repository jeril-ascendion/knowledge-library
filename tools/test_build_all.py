import hashlib
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / "dist"
AGENT_DIR = DIST / "knowledge-graph" / "agent" / "v1"
BUILDER = REPO_ROOT / "tools" / "build_all.py"


def _run_build_all():
    subprocess.run(
        ["python3", str(BUILDER)],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
    )


@pytest.fixture(scope="session")
def built():
    """Run build_all.py once. Slow: ~3-5 min due to BGE encoding."""
    _run_build_all()
    return True


# ─────────────────────────── Tests ──────────────────────────────


@pytest.mark.slow
def test_build_all_completes_cleanly(built):
    """build_all.py runs without raising. The fixture itself enforces this."""
    assert True


@pytest.mark.slow
def test_static_site_homepage_exists(built):
    """Sentinel for generate.py output."""
    assert (DIST / "index.html").exists(), "generate.py output missing"


@pytest.mark.slow
def test_llms_txt_at_site_root(built):
    """llms.txt at dist/llms.txt, NOT under knowledge-graph/."""
    assert (DIST / "llms.txt").exists(), "llms.txt not at site root"
    assert not (AGENT_DIR / "llms.txt").exists(), "llms.txt incorrectly under agent dir"


@pytest.mark.slow
def test_agent_endpoint_json_artifacts_exist(built):
    """All 4 JSON artifacts in agent/v1/."""
    expected = ["chunks.json", "index.json", "schema.json", "gold_references.json"]
    for name in expected:
        path = AGENT_DIR / name
        assert path.exists(), f"missing {path.relative_to(REPO_ROOT)}"
        assert path.stat().st_size > 0, f"empty {path.relative_to(REPO_ROOT)}"


@pytest.mark.slow
def test_agent_endpoint_binary_artifacts_exist(built):
    """vectors.bin (1.1 MB expected) + index.bin (1.2 MB expected)."""
    vec = AGENT_DIR / "vectors.bin"
    idx = AGENT_DIR / "index.bin"
    assert vec.exists() and vec.stat().st_size == 1112072, f"vectors.bin wrong size or missing"
    assert idx.exists() and idx.stat().st_size > 1000000, f"index.bin wrong size or missing"


@pytest.mark.slow
def test_build_failure_propagates():
    """If a builder script fails, build_all.py fails with non-zero exit.
    Test by temporarily renaming a builder so it isn't found."""
    chunks_builder = REPO_ROOT / "tools" / "build_chunks.py"
    backup = REPO_ROOT / "tools" / "build_chunks.py.bak"

    chunks_builder.rename(backup)
    try:
        result = subprocess.run(
            ["python3", str(BUILDER)],
            cwd=REPO_ROOT,
            capture_output=True,
        )
        assert result.returncode != 0, "build_all.py should fail when build_chunks.py is missing"
    finally:
        backup.rename(chunks_builder)


@pytest.mark.slow
def test_text_artifacts_byte_deterministic():
    """All text outputs (chunks.json, index.json, schema.json, gold_references.json, llms.txt) are byte-identical across two consecutive runs of build_all.py.

    Note: vectors.bin and index.bin determinism is covered by T2.2's slow tests; this just verifies the orchestrator preserves it for the text artifacts."""
    text_files = [
        DIST / "llms.txt",
        AGENT_DIR / "chunks.json",
        AGENT_DIR / "index.json",
        AGENT_DIR / "schema.json",
        AGENT_DIR / "gold_references.json",
    ]

    _run_build_all()
    h1 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in text_files}

    _run_build_all()
    h2 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in text_files}

    mismatches = [name for name in h1 if h1[name] != h2[name]]
    assert not mismatches, f"non-deterministic outputs: {mismatches}"


@pytest.mark.slow
def test_build_step_order_documented():
    """Sanity check: build_all.py source mentions all 8 builder names in code-readable order.
    Catches accidental removal of a step."""
    source = BUILDER.read_text()
    expected_order = [
        "seed_content.py",
        "generate.py",
        "build_chunks.py",
        "build_vector_index.py",
        "build_index_json.py",
        "build_schema_json.py",
        "build_gold_references_json.py",
        "build_llms_txt.py",
    ]
    last_pos = -1
    for name in expected_order:
        pos = source.find(name)
        assert pos > last_pos, f"build step '{name}' missing or out of order in build_all.py"
        last_pos = pos
