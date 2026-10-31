#!/usr/bin/env python3
"""Reject actual implementation and source-pin corruptions on private copies.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
import json
from pathlib import Path
import runpy
import shutil
import tempfile

HERE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def discriminating_cases(namespace):
    function = namespace["squared_envelope"]
    for s, t, wanted in [(0, 0, 0), (0, 4, 4), (3, 0, 3),
                         (2, 0, 0), (0, 1, 0)]:
        _, lo, hi = function(s, t)
        check(lo <= wanted <= hi, "exact endpoint was corrupted")
    branch, lo, hi = function(1, 2)
    check(branch == "high" and F(37, 10) < lo <= hi < F(19, 5),
          "closed asymmetric threshold was corrupted")
    branch, lo, hi = function(1, 1)
    check(branch == "low" and F(1, 10) < lo <= hi < F(1, 5),
          "low cubic root was corrupted")


def oracle_boundary_mutant(root):
    source = (HERE / "independent.py").read_text()
    old = ("if (count == 1 and hi - lo <= tolerance\n"
           "                and evaluate(original, lo) != 0 and evaluate(original, hi) != 0):")
    check(source.count(old) == 1, "oracle mutation anchor is not unique")
    expected = (F(0), F(0))
    case = F(0), 4 - F(1, 2 ** 100)
    current = runpy.run_path(str(HERE / "independent.py"))
    check(current["oracle"](*case) == expected, "oracle baseline boundary failure")
    path = root / "oracle-endpoint-mutant.py"
    path.write_text(source.replace(old, "if count == 1 and hi - lo <= tolerance:"))
    mutant = runpy.run_path(str(path))
    check(mutant["oracle"](*case) != expected, "old endpoint bug was not exposed")
    return 1


def run():
    source = (HERE / "envelope.py").read_text()
    discriminating_cases(runpy.run_path(str(HERE / "envelope.py")))
    changes = [
        ("h <= (t - 2) ** 2", "h < (t - 2) ** 2"),
        ("h >= (t - 2) ** 2", "h <= (t - 2) ** 2"),
        ("min(qlo, clo), min(qhi, chi)", "max(qlo, clo), max(qhi, chi)"),
        ("t, 3, 4, bits", "t, 0, 1, bits"),
        ("if s >= 3:", "if s >= 2:"),
    ]
    with tempfile.TemporaryDirectory(prefix="asymmetric-phase-mutants-") as directory:
        root = Path(directory)
        oracle_mutants = oracle_boundary_mutant(root)
        for index, (old, new) in enumerate(changes):
            check(source.count(old) == 1, "mutation anchor is not unique")
            path = root / f"mutant{index}.py"
            path.write_text(source.replace(old, new))
            try:
                discriminating_cases(runpy.run_path(str(path)))
            except ValueError:
                continue
            raise ValueError("implementation mutation survived: " + old)
        package = root / "research/asymmetric-tensor-phase"
        package.mkdir(parents=True)
        for name in ("verify.py", "envelope.py", "SOURCES.json"):
            shutil.copyfile(HERE / name, package / name)
        sources = json.loads((HERE / "SOURCES.json").read_text())
        inputs = [row for row in sources["files"] if row["usage"] == "input"]
        for row in inputs:
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / row["path"], target)
        namespace = runpy.run_path(str(package / "verify.py"))
        check(namespace["authenticate"]() == len(inputs), "source-copy control failed")
        for row in inputs:
            path = root / row["path"]
            saved = path.read_bytes()
            path.write_bytes(saved + b"\nactual corruption\n")
            try:
                namespace["authenticate"]()
            except ValueError:
                path.write_bytes(saved)
                continue
            raise ValueError("source corruption survived")
        expected = json.loads((HERE / "RESULT.json").read_text())
        receipt = package / "RESULT.json"
        receipt.write_text(json.dumps(expected))
        namespace["validate_receipt"](expected)
        altered = dict(expected, source_files_authenticated=-1)
        receipt.write_text(json.dumps(altered))
        try:
            namespace["validate_receipt"](expected)
        except ValueError:
            pass
        else:
            raise ValueError("receipt corruption survived")
    return {"actual_code_mutants_rejected": len(changes),
            "actual_oracle_mutants_rejected": oracle_mutants,
            "actual_source_corruptions_rejected": len(inputs),
            "actual_receipt_corruptions_rejected": 1}


if __name__ == "__main__":
    print("PASS_ASYMMETRIC_PHASE_MUTATIONS " + json.dumps(run(), sort_keys=True))
