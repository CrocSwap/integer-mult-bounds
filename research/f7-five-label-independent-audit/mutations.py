#!/usr/bin/env python3
"""Reject semantic mutations without relying on the stored receipt or hashes.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    source = (Path(__file__).resolve().parent / "verify.py").read_text(encoding="utf-8")
    mutations = {
        "missing_position": ("combinations(range(12), 4)", "combinations(range(11), 4)"),
        "missing_pairings": ("enumerate(rest):", "enumerate(rest[:1]):"),
        "early_simple_filter_removed": ("if len(set(points)) != 12:", "if False:"),
        "universality_as_cardinality": (
            "return {x ^ y for x in points for y in points} == set(range(32))",
            "return len(set(points)) == 12"),
        "merged_class_supports": (
            "sum(comb(n, 2) for n in sizes) - sum(supports)",
            "sum(comb(n, 2) for n in sizes) - len(support(classes[0]) | support(classes[1]))"),
        "cap_ten": ("def check_target(word, mask=31, cap=11):", "def check_target(word, mask=31, cap=10):"),
        "low_weight_admitted": ("require(mask in MASKS, \"weight\")", "require(0 < mask < 32, \"weight\")"),
        "class_zero_only": ("for parity in (0, 1)]", "for parity in (0, 0)]"),
    }
    with tempfile.TemporaryDirectory(prefix="five-label-audit-") as directory:
        path = Path(directory) / "verify.py"
        # Both positive and negative runs use --emit-receipt, bypassing RESULT.
        path.write_text(source, encoding="utf-8", newline="\n")
        command = [sys.executable, "-I", "-O", "-W", "error", "-B", str(path), "--emit-receipt"]
        baseline = subprocess.run(command, capture_output=True, timeout=30)
        if baseline.returncode:
            raise ValueError("positive control failed: " + baseline.stderr.decode(errors="replace"))
        for name, (old, new) in mutations.items():
            if source.count(old) != 1:
                raise ValueError("mutation target is not unique: " + name)
            path.write_text(source.replace(old, new), encoding="utf-8", newline="\n")
            result = subprocess.run(command, capture_output=True, timeout=30)
            if result.returncode == 0 or b"ValueError:" not in result.stderr:
                raise ValueError("mutation was not semantically rejected: " + name)
            print("REJECTED", name, result.stderr.decode(errors="replace").splitlines()[-1])
    print("PASS_F7_INDEPENDENT_MUTATIONS count=8 receipt_comparison=disabled")


if __name__ == "__main__":
    main()
