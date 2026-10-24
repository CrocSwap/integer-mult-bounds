#!/usr/bin/env python3
"""Show current first steps and preserve the frozen task-picker output.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Arguments and selection are delegated to the historical picker CLI.
"""
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts/choose_research_task.py"
check_catalog_files = runpy.run_path(str(LEGACY))["check_catalog_files"]


def resolve_current_first_steps(result, root):
    """Resolve generic orientation at the CLI boundary; keep the source card."""
    old = ["python3", "-B", "scripts/research_baseline.py"]
    current = "scripts/research_selected_baseline.py"
    cards = [card for card in result["suggestions"]
             if card["first_step"]["command"] == old]
    if not cards:
        return []
    omitted = check_catalog_files(root, [
        (current, "missing current first-step script: " + current),
    ])
    for card in cards:
        original = card["first_step"]
        card["catalog_first_step"] = original
        card["first_step"] = {**original, "command": ["python3", "-B", current]}
        card["first_step_resolution"] = (
            "The current CLI uses the selected-certificate baseline for generic "
            "orientation. catalog_first_step is the exact frozen card entry. "
            "The task, scientific checks and acceptance gate are unchanged."
        )
    return omitted


def main():
    child = subprocess.run([sys.executable, "-B", str(LEGACY), *sys.argv[1:]],
                           capture_output=True, text=True, encoding="utf-8")
    if child.returncode or any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        sys.stdout.write(child.stdout)
        sys.stderr.write(child.stderr)
        return child.returncode
    try:
        result = json.loads(child.stdout)
        omitted = resolve_current_first_steps(result, ROOT)
        if omitted:
            sparse = result.setdefault("sparse_checkout", {"omitted_catalogue_paths": []})
            sparse["omitted_current_first_step_paths"] = omitted
            sparse["scope"] = (
                "These absent regular files match HEAD and skip-worktree index entries. "
                "Materialize the chosen task's inputs before running it; this validates "
                "first-step references, not replay dependencies."
            )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write("current first-step resolution failed: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
