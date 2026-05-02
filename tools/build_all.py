"""Orchestrate the full ascendion.engineering build.

Runs all 8 builders sequentially as subprocesses. Any failure aborts
the run with a non-zero exit. Subprocess stdout/stderr stream through
so the user can watch progress (notably the ~3 min BGE encoding step).
"""

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

BUILD_STEPS = [
    ("seed taxonomy stubs",       ["python3", "tools/seed_content.py"]),
    ("build static site",         ["python3", "tools/generate.py", "--src", "content", "--out", "dist", "--clean"]),
    ("build chunks",              ["python3", "tools/build_chunks.py"]),
    ("build vector index (slow)", ["python3", "tools/build_vector_index.py"]),
    ("build index.json",          ["python3", "tools/build_index_json.py"]),
    ("build schema.json",         ["python3", "tools/build_schema_json.py"]),
    ("build gold_references.json",["python3", "tools/build_gold_references_json.py"]),
    ("build llms.txt",            ["python3", "tools/build_llms_txt.py"]),
]


def main():
    total = len(BUILD_STEPS)
    for i, (description, command_args) in enumerate(BUILD_STEPS):
        print(f"[{i+1}/{total}] {description}...")
        subprocess.run(command_args, check=True, cwd=REPO_ROOT)

    print("Build complete: static site + agent endpoint at dist/knowledge-graph/agent/v1/ + dist/llms.txt")


if __name__ == "__main__":
    main()
