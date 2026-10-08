#!/usr/bin/env python3
"""Compile the row theorem from fresh dependency oleans in pinned Mathlib."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
EXPECTED = {
    "join_split", "role_join", "group_join", "merge_split", "merge_uniform",
    "framed_rows", "restrict_pad", "padding_commutes",
    "padded_endpoint_restrict", "padded_endpoint_blank",
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mathlib-project", type=Path, required=True)
    parser.add_argument("--lean-bin", type=Path, required=True)
    args = parser.parse_args()
    project = args.mathlib_project.resolve()
    lean_bin = args.lean_bin.resolve()
    sources = [HERE.parent / "framed" / n for n in ("DirtyWrapper.lean", "FramedXor.lean")]
    sources.append(HERE / "RowInterchange.lean")
    for source in sources:
        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")
    env = os.environ.copy()
    env["PATH"] = str(lean_bin) + os.pathsep + env.get("PATH", "")
    version = subprocess.check_output([str(lean_bin / "lean"), "--version"], text=True)
    if not re.search(r"version 4\.21\.0(?:,|\s)", version):
        raise SystemExit(f"Expected Lean4.21.0, received {version.strip()}")
    logs = []
    with tempfile.TemporaryDirectory(prefix="row-semantics-") as tmp:
        root = Path(tmp)
        env["LEAN_PATH"] = str(root)
        for source in sources:
            local = root / source.name
            shutil.copy2(source, local)
            result = subprocess.run(
                [str(lean_bin / "lake"), "env", "lean", "--root=" + str(root),
                 "-o", str(local.with_suffix(".olean")), str(local)],
                cwd=project, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
            logs.append(f"SOURCE {source.name}\n{result.stdout}")
            if result.returncode or re.search(r"\b(sorryAx|native_decide|Lean\.ofReduceBool)\b", result.stdout):
                (HERE / "verification.log").write_text("\n".join(logs))
                raise SystemExit(f"Compilation or axiom audit failed: {source.name}")
        row_log = result.stdout
        declarations = re.findall(r"'RowInterchange\.([^']+)' depends on axioms: \[([^\]]*)\]", row_log)
        if {name for name, _ in declarations} != EXPECTED:
            raise SystemExit("Unexpected or incomplete row declaration audit")
        for name, axioms in declarations:
            if set(filter(None, (x.strip() for x in axioms.split(',')))) - {"propext", "Quot.sound", "Classical.choice"}:
                raise SystemExit(f"Nonstandard axiom: {name}: {axioms}")
    (HERE / "verification.log").write_text("\n".join(logs))
    receipt = {
        "status": "PASS", "toolchain": version.strip(), "row_theorems_audited": len(EXPECTED),
        "axioms": {name: [x.strip() for x in axioms.split(',') if x.strip()] for name, axioms in declarations},
        "source_sha256": {source.name: hashlib.sha256(source.read_bytes()).hexdigest() for source in sources},
        "scope": "Finite cyclic-row bijection; framed semantic endpoint under explicit scalar/gauge premises; zero-padding restriction. No concrete compiler trace or tape-cost theorem.",
    }
    (HERE / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
