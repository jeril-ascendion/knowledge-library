#!/usr/bin/env python3
"""T3.3 — agent endpoint gold references registry builder.

Output: dist/knowledge-graph/agent/v1/gold_references.json (byte-deterministic)

Flattens GOLD_REFERENCES dict from tools/generate.py into a list sorted
alphabetically by id. Each entry has 9 string fields: id, label, url,
organization, license, last_verified, summary, summary_author, summary_date.
"""

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
OUT_PATH = REPO_ROOT / "dist" / "knowledge-graph" / "agent" / "v1" / "gold_references.json"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    generate = _load("generate", TOOLS_DIR / "generate.py")

    refs_dict = generate.GOLD_REFERENCES
    references = [refs_dict[k] for k in sorted(refs_dict.keys())]

    output = {
        "schema_version": "1.0",
        "references": references,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, sort_keys=True, indent=2)
        f.write("\n")

    print(
        f"gold_references.json: {len(references)} entries -> "
        f"{OUT_PATH.relative_to(REPO_ROOT)}"
    )


if __name__ == "__main__":
    main()
