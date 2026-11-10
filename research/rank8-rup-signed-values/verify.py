#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the new representation and complete retained CLI equivalence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("signed_adapter", HERE / "adapter.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load local adapter")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
require = adapter.require


def representation_controls() -> int:
    reads = 0
    for size in range(1, 7):
        for state in itertools.product((-1, 0, 1), repeat=size):
            values = [0] * (2 * size + 1)
            for index, value in enumerate(state, 1):
                values[index], values[-index] = value, -value
            for literal in range(-size, size + 1):
                if literal:
                    expected = state[abs(literal) - 1] * (1 if literal > 0 else -1)
                    require(values[literal] == expected, "signed value invariant")
                    reads += 1
            for index in range(1, size + 1):
                values[index] = values[-index] = 0
            require(not any(values), "trail reset invariant")
    return reads


def differential_controls() -> int:
    old = adapter.load_source(False)["rup_check"]
    new = adapter.load_source(True)["rup_check"]
    count = 0
    # Every normalized two-variable clause and every ordered formula of <=2 clauses.
    clauses = [tuple(sign * (i + 1) for i, sign in enumerate(signs) if sign)
               for signs in itertools.product((-1, 0, 1), repeat=2)]
    proofs = [" ".join(map(str, (*clause, 0))) for clause in clauses]
    proofs += ["", "c comment", "d 1 0", "x 0", "1", "0 0", "3 0", "1 1 0"]
    formulas = [()] + [(clause,) for clause in clauses]
    formulas += list(itertools.product(clauses, repeat=2))
    for formula in formulas:
        for first in proofs:
            for second in ("0", "1 0", "-1 0"):
                for limit in (None, 1):
                    lines = [first, second]
                    require(old(formula, 2, lines, limit) == new(formula, 2, lines, limit),
                            "RUP decision/parser/count mismatch")
                    count += 1
    return count


def admission_controls(scratch: Path) -> int:
    path, source = adapter.authenticated_source()
    changed = source.replace("v = value(l)", "v = broken(l)", 1)
    try:
        adapter.signed_source(changed)
    except ValueError:
        pass
    else:
        raise ValueError("changed replacement site accepted")
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    controls = 1
    with tempfile.TemporaryDirectory(dir=scratch, prefix="source-controls-") as name:
        root = Path(name)
        for row in inputs:
            destination = root / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((adapter.ROOT / row["path"]).read_bytes())
        for row in inputs:
            destination = root / row["path"]
            original = destination.read_bytes()
            destination.write_bytes(original + b"\ncorruption\n")
            try:
                adapter.authenticated_source(root)
            except ValueError:
                controls += 1
            else:
                raise ValueError(f"changed input accepted: {row['path']}")
            destination.write_bytes(original)
        missing = root / inputs[-1]["path"]
        missing.unlink()
        try:
            adapter.authenticated_source(root)
        except ValueError:
            controls += 1
        else:
            raise ValueError("missing proof accepted")
    require(path.is_file(), "source disappeared")
    return controls


def command(engine: str, unit: str, output: Path) -> list[str]:
    path = adapter.ROOT / adapter.SOURCE if engine == "baseline" else HERE / "adapter.py"
    return [sys.executable, "-I", "-B", str(path), "--live", unit, "--out", str(output)]


def run(engine: str, unit: str, output: Path) -> tuple[bytes, dict]:
    completed = subprocess.run(command(engine, unit, output), capture_output=True,
                               timeout=150, check=False)
    require(completed.returncode == 0,
            f"{engine}/{unit} exit {completed.returncode}: {completed.stderr[-2000:]!r}")
    require(not completed.stderr, f"unexpected stderr: {completed.stderr!r}")
    payload = json.loads(output.read_text())
    require(payload["fails"] == [], "retained scientific check failed")
    require(b"PASS_COMPLEX_RANK8_DECODER_RIGIDITY:" in completed.stdout,
            "incomplete retained replay")
    return completed.stdout, payload


def complete_equivalence(unit: str, scratch: Path) -> dict:
    adapter.authenticated_source()
    with tempfile.TemporaryDirectory(dir=scratch, prefix=f"complete-{unit}-") as name:
        root = Path(name)
        before, left = run("baseline", unit, root / "baseline.json")
        after, right = run("candidate", unit, root / "candidate.json")
    require(before == after and left == right, "complete output/certificate mismatch")
    return {"unit": unit, "checks": len(left["log"]), "fails": 0,
            "stdout_sha256": hashlib.sha256(before).hexdigest(),
            "certificate_sha256": hashlib.sha256(json.dumps(left, sort_keys=True).encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", choices=("P112", "P120"))
    args = parser.parse_args()
    scratch = Path(tempfile.gettempdir())
    result = {"status": "PASS_RANK8_RUP_SIGNED_VALUES", "no_new_kappa": True}
    if args.unit:
        result["complete"] = complete_equivalence(args.unit, scratch)
    else:
        result["literal_reads"] = representation_controls()
        result["differential_cases"] = differential_controls()
        result["admission_controls"] = admission_controls(scratch)
    result["files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
