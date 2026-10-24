#!/usr/bin/env python3
"""Run the two source-bound checks without modifying frozen evidence.

Yiyang (@Lyy-iiis), substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import json
import subprocess
import sys
from tempfile import TemporaryDirectory


def main():
    here = Path(__file__).resolve().parent
    source = here.parents[1] / "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
    with TemporaryDirectory(prefix="border-paid-precision-") as temporary:
        temporary = Path(temporary)
        subprocess.run([
            sys.executable, "-I", "-B", "-O",
            str(here / "paid-sensitivity/check_paid_sensitivity.py"),
            "--expected", str(here / "paid-sensitivity/PAID-SENSITIVITY.json.gz"),
            "--out", str(temporary / "replayed.json.gz"),
        ], check=True)
        subprocess.run([
            sys.executable, "-I", "-B", "-O",
            str(here / "inverse-interface/verify.py"),
        ], check=True)
        for checker, output_flag, frozen, output in (
            ("inverse-interface/independent_centers.py", "--output",
             "inverse-interface/INDEPENDENT-CENTERS.json", "centers.json"),
            ("independent-review/invariance/check_invariance.py", "--out",
             "independent-review/invariance/INVARIANCE.json", "invariance.json"),
        ):
            destination = temporary / output
            subprocess.run([
                sys.executable, "-I", "-B", "-O", str(here / checker),
                "--source", str(source), output_flag, str(destination),
            ], check=True)
            def canonical(path):
                return json.dumps(json.loads(path.read_text()), sort_keys=True,
                                  separators=(",", ":"), allow_nan=False)
            if canonical(destination) != canonical(here / frozen):
                raise ValueError("Independent frozen receipt differs: " + frozen)
    print("PASS_TWO_FULL_BORDER_PAID_PRECISION_AND_COHERENT_INVERSE_NO_KAPPA")


if __name__ == "__main__":
    main()
