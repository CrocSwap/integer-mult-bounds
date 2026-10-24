#!/usr/bin/env python3
"""Require semantic mutants and private source/receipt faults to fail.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = (PACKAGE / "verify.py").read_text(encoding="utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def semantic_mutations():
    cases = (
        ("overlapping interiors", "if left_used & right_used == shared:",
         "if True:", "calibrate"),
        ("missing coordinate", "for coordinate in range(n):",
         "for coordinate in range(n - 1):", "calibrate"),
        ("missing closing edge", "zip(points, points[1:] + points[:1])",
         "zip(points, points[1:])", "controls"),
        ("bit-0 grouping", "(x & mask).bit_count() % 2 == bit",
         "(x & 1) == bit", "controls"),
        ("cross-class support", "support_bits(group).bit_count()",
         "support_bits(points).bit_count()", "controls"),
        ("cap ten", "def check_target(points, mask, cap=11):",
         "def check_target(points, mask, cap=10):", "controls"),
    )
    for name, old, new, entry in cases:
        require(SOURCE.count(old) == 1, "mutation site: " + name)
        namespace = {"__file__": str(PACKAGE / "verify.py"), "__name__": "audit_mutant"}
        exec(compile(SOURCE.replace(old, new), str(PACKAGE / "verify.py"), "exec"), namespace)
        try:
            namespace[entry]()
        except ValueError as error:
            print("REJECT_MUTANT", name, str(error))
        else:
            raise ValueError("surviving mutant: " + name)
    return len(cases)


def integrity_faults():
    with tempfile.TemporaryDirectory(prefix="f7-audit-controls-") as temp:
        root = Path(temp)
        package = root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package)
        manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
        for row in manifest["files"]:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)

        def reject_cli(reason):
            result = subprocess.run(
                [sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                cwd=root, text=True, encoding="utf-8", capture_output=True, timeout=60)
            require(result.returncode != 0 and reason in result.stderr,
                    "private fault was not rejected at expected gate: " + reason)

        proof = root / "research/f7-five-label-sharp-cap/README.md"
        original = proof.read_bytes()
        proof.write_bytes(original + b"\nchanged reviewed proof\n")
        reject_cli("source drift: research/f7-five-label-sharp-cap/README.md")
        proof.write_bytes(original)
        receipt_path = package / "RESULT.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        require(type(receipt["calibration"][0]["cycles"]) is int and
                receipt["calibration"][0]["cycles"] == 1, "typed fault fixture")
        receipt["calibration"][0]["cycles"] = True
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        reject_cli("receipt mismatch")
    return 2


def main():
    mutations = semantic_mutations()
    faults = integrity_faults()
    print(f"PASS_F7_AUDIT_CONTROLS semantic_mutants={mutations} private_faults={faults}")


if __name__ == "__main__":
    main()
