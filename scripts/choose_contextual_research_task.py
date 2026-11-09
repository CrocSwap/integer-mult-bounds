#!/usr/bin/env python3
"""Show catalogue assessment drift alongside the current task-picker receipt.

The frozen current and legacy pickers retain their source and behavior.
Sricharan Vagvala, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
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
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write("catalogue selection comparison failed: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
