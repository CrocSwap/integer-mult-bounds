#!/usr/bin/env python3
"""Exercise real verifier entry points on private, deliberately changed copies.

Krzysztof Wojt with OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


PACKAGE = Path(__file__).resolve().parent


def run_source(source, optimized, directory):
    path = directory / "mutant.py"
    path.write_text(source, encoding="utf-8")
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if optimized:
        command.append("-O")
    return subprocess.run(command + [str(path)], text=True, capture_output=True, timeout=20)


def main():
    source = (PACKAGE / "verify.py").read_text(encoding="utf-8")
    independent = (PACKAGE / "independent.py").read_text(encoding="utf-8")
    cases = [
        (source, "C = (2, 4, 1)", "C = (1, 2, 4)", "cycle order"),
        (source, "FACTORS = ((7, -6, 1)", "FACTORS = ((8, -6, 1)", "expanded polynomial"),
        (source, "ell = {E: 6,", "ell = {E: 5,", "p(L)B=0"),
        (source, "b = {E: 2, C: -1, c2: -1}", "b = {E: 2, C: -1, c2: 1}", "B^2=3B"),
        (source, "excess * excess <= 162 *", "excess * excess <= 225 *", "six-to-one"),
        (independent, "[7, -6, 1],", "[8, -6, 1],", "RuntimeError"),
    ]
    rejected = 0
    with tempfile.TemporaryDirectory(prefix="three-cycle-cut-controls-") as name:
        directory = Path(name)
        for original, before, after, expected in cases:
            if original.count(before) != 1:
                raise ValueError(f"mutation anchor is not unique: {before}")
            for optimized in (False, True):
                result = run_source(original.replace(before, after), optimized, directory)
                if result.returncode == 0 or expected not in result.stderr:
                    raise ValueError(f"corruption accepted or wrong failure: {before}, O={optimized}: {result.stderr}")
                rejected += 1
        # Reversing the same three-cycle is legal and must not be rejected.
        for optimized in (False, True):
            result = run_source(source.replace("C = (2, 4, 1)", "C = (4, 1, 2)"), optimized, directory)
            if result.returncode or json.loads(result.stdout)["status"] != "PASS_THREE_CYCLE_CUT_CEILING":
                raise ValueError(f"inverse-cycle positive control failed: {result.stderr}")
    print(json.dumps({"status": "PASS_CLI_CONTROLS", "rejected_corruptions": rejected,
                      "inverse_cycle_positive_runs": 2}, sort_keys=True))


if __name__ == "__main__":
    main()
