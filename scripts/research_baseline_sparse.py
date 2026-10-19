#!/usr/bin/env python3
"""Name the selected inputs a sparse checkout omits before research_baseline.py.

In a sparse checkout, ``scripts/research_baseline.py`` stops at the first absent
selected input with ``Invalid selected file: ...`` and does not say which
directories it needs. This read-only preflight lists every input that check
reads and prints the ``git sparse-checkout add`` command that materializes them.

An absent path counts as a sparse omission only under the chooser's PR3102
contract (``choose_research_task.check_catalog_files``): a stage-zero regular
skip-worktree entry whose blob matches HEAD. An ordinary deletion, staged drift
or unknown path raises the same ``Invalid selected file`` error. Byte drift in
present files is left to ``research_baseline.py``. Nothing is verified here.

This is a separate script so that the baseline and its tests, which research
packages pin as live inputs, keep their bytes.

Exit codes: 0 when no selected input is omitted, 2 when some are.

Douglas Colkitt, with Claude Opus 5.5 assistance. Apache-2.0. The sparse
contract follows Arham-Tahir64's PR3102.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from choose_research_task import check_catalog_files

ROOT = Path(__file__).resolve().parents[1]
SELECTED = "certificates/selected-result.json"


def selected_inputs(record, root=ROOT):
    """Repository paths the selected-record check reads, before it reads them."""
    names = [record["certificate"], record["source_manifest"], record["proof"],
             record["review"], record["validation"], *record["proof_supplements"]]
    check_catalog_files(root, [(names[1], "Invalid selected file: " + names[1])])
    manifest = root / record["source_manifest"]
    if manifest.is_file():
        raw = manifest.read_bytes()
    else:  # a sparse omission whose index blob matches HEAD (checked above)
        raw = subprocess.run(["git", "cat-file", "blob", "HEAD:" + record["source_manifest"]],
                             cwd=root, check=True, capture_output=True).stdout
    inventory = json.loads(raw)
    if inventory.get("format") == "repository-packages-sha256-v1":
        names += inventory["files"]
    else:
        parent = Path(record["source_manifest"]).parent
        names += [(parent / name).as_posix() for name in inventory["files"]]
    return sorted(set(names))


def sparse_omissions(record, root=ROOT):
    """Selected inputs absent only because this is a sparse checkout."""
    names = selected_inputs(record, root)
    return check_catalog_files(root, [(name, "Invalid selected file: " + name) for name in names])


def materialize_command(omitted):
    """Cone-mode directories covering the omitted files (one research package each)."""
    dirs = set()
    for name in omitted:
        parts = name.split("/")
        if parts[0] == "research" and len(parts) > 2:
            dirs.add("/".join(parts[:2]))
        else:
            dirs.add("/".join(parts[:-1]) or ".")
    return ["git", "sparse-checkout", "add", *sorted(dirs)]


def report(record, root=ROOT):
    omitted = sparse_omissions(record, root)
    if not omitted:
        return 0, {
            "status": "NO_SPARSE_SELECTED_OMISSIONS",
            "next": ["python3", "-B", "scripts/research_baseline.py"],
            "scope": "Every selected input is present. Nothing was verified; run the baseline next.",
        }
    return 2, {
        "status": "SPARSE_SELECTED_INPUTS_ABSENT",
        "omitted_files": len(omitted), "first_omitted": omitted[:5],
        "materialize": materialize_command(omitted),
        "scope": "This sparse checkout omits selected inputs (skip-worktree entries matching HEAD). "
                 "Run the materialize command, then scripts/research_baseline.py; nothing was verified.",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    record = json.loads((args.root / SELECTED).read_bytes())
    code, result = report(record, args.root)
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
