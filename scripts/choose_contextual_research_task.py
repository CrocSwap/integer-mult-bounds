#!/usr/bin/env python3
"""Show catalogue assessment drift alongside the current task-picker receipt.

The frozen current and legacy pickers retain their source and behavior.
Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
Direct-theorem routing and sparse-entry checks with OpenAI Codex assistance.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "scripts/choose_current_research_task.py"


def catalog_selection_context(result, root):
    """Compare declared context, without interpreting it as scientific coverage."""
    documents = []
    for name, digest_key in (
        ("docs/research/agent-task-catalog.json", "catalog_sha256"),
        ("certificates/selected-result.json", "selected_record_sha256"),
    ):
        raw = (root / name).read_bytes()
        if sha256(raw).hexdigest() != result[digest_key]:
            raise ValueError("input changed since task selection: " + name)
        documents.append(json.loads(raw))
    catalog, selected = documents
    context = catalog.get("selection_context")
    if context is not None and not isinstance(context, dict):
        raise ValueError("catalogue selection_context must be an object")
    differences, missing = {}, []
    for field, selected_field in (
        ("kappa", "kappa"), ("source_commit", "audited_source_head"),
        ("review", "review"),
    ):
        before = (context or {}).get(field)
        after = selected.get(selected_field)
        if before is None or after is None:
            missing.append(field)
            continue
        if not all(isinstance(value, str) and value.strip() for value in (before, after)):
            raise ValueError("invalid selection context field: " + field)
        if field == "kappa":
            try:
                equal = Fraction(before) == Fraction(after)
            except (ValueError, ZeroDivisionError) as exc:
                raise ValueError("invalid selection context kappa") from exc
        else:
            equal = before == after
        if not equal:
            differences[field] = {"catalog": before, "selected": after}
    return {
        "context": context,
        "matches_selected": False if differences else (None if missing else True),
        "differences": differences,
        "uncompared_fields": missing,
        "scope": (
            "Compare only kappa, source_commit/audited_source_head and review. "
            "Missing fields are unknown. The catalogue context is historical; "
            "use selected for the current result and replay. Matching metadata "
            "does not establish current task coverage or scientific validation. "
            "Input hashes bind this comparison to the picker receipt, not the "
            "complete selected source closure."
        ),
    }


def resolve_direct_first_steps(result, root):
    """Validate the direct entry point before replacing historical orientation."""
    if result["selected"]["reproduce"] != "make nov24-direct-verify":
        return []
    previous = ["python3", "-B", "scripts/research_selected_baseline.py"]
    cards = [card for card in result["suggestions"]
             if card["first_step"]["command"] == previous]
    if not cards:
        return []
    direct = "scripts/verify_nov24_direct.py"
    check_catalog_files = run_path(str(root / "scripts/choose_research_task.py"))["check_catalog_files"]
    omitted = check_catalog_files(root, [(direct, "missing direct first-step script: " + direct)])
    # Resolve all references before modifying a suggestion. The existing sparse
    # contract distinguishes a HEAD-matching omission from deletion or drift.
    for card in cards:
        card.setdefault("catalog_first_step", card["first_step"])
        card["first_step"] = {
            "command": ["python3", "-B", direct],
            "expected": "PASS_NOV24_DIRECT_COROLLARY",
            "inspect": "Read the direct theorem, fixed witness and strict endpoint.",
            "scope": "Selected source and exponent checks for the November multiplier.",
        }
        card["first_step_resolution"] = (
            "The original catalogue step remains in catalog_first_step. "
            "Use the direct theorem for current orientation; retain any follow_up_steps. "
            "Materialize omitted entry points before execution."
        )
    return omitted


def main():
    child = subprocess.run([sys.executable, "-B", str(CURRENT), *sys.argv[1:]],
                           capture_output=True, text=True, encoding="utf-8")
    if child.returncode or any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        sys.stdout.write(child.stdout)
        sys.stderr.write(child.stderr)
        return child.returncode
    sys.stderr.write(child.stderr)
    try:
        result = json.loads(child.stdout)
        result["catalog_selection"] = catalog_selection_context(result, ROOT)
        omitted = resolve_direct_first_steps(result, ROOT)
        if omitted:
            sparse = result.setdefault("sparse_checkout", {"omitted_catalogue_paths": []})
            sparse["omitted_current_first_step_paths"] = sorted(set(
                sparse.get("omitted_current_first_step_paths", []) + omitted))
            sparse["scope"] = (
                "These absent regular files match HEAD and skip-worktree index entries. "
                "Materialize the chosen task's inputs before running it; this validates "
                "first-step references, not replay dependencies."
            )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write("contextual task resolution failed: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
