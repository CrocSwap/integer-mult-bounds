"""Independent exact-power controls and deterministic certificate replay.

This does not execute Lean or claim that source checks are a kernel proof.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from certificate import GRID, profile, propose, propose_chain, check, render_lean, need


def calibration():
    cases, digest = 0, sha256()
    # Complete declared domain, tested against direct integer powers rather
    # than another square-root implementation. The exact exponent-one endpoint
    # is handled separately and is not silently truncated to its low bits.
    for denominator in range(2, 13):
        for numerator in range(1, denominator + 1):
            x = Q(numerator, denominator)
            for bits in range(1, 6):
                for p in range(2**bits):
                    ns = propose_chain(x, p, bits, GRID)
                    upper = Q(ns[-1], GRID)
                    need(x**p <= upper**(2**bits), "direct power calibration")
                    digest.update(f"{numerator}/{denominator}:{p}/{2**bits}:{ns[-1]}\n".encode())
                    cases += 1
    return {"cases": cases, "domain": "1<=r<=m, 2<=m<=12, 1<=k<=5, 0<=p<2^k",
            "trace_sha256": digest.hexdigest()}


def replay(root=HERE):
    counts = profile(root)
    data = json.loads((root / "DYADIC.json").read_bytes())
    result = check(data, counts)
    need(data == propose(counts), "proposal replay")
    need((root / "lean/SelectedMoment.lean").read_text() == render_lean(data, counts),
         "Lean/certificate semantic binding")
    # A second method checks each FINAL upper directly at the actual non-dyadic
    # source exponent. It is not needed as a formal hypothesis of the Lean proof.
    for rank, value in result["upper_numerators"].items():
        need(pow(int(rank), 9983) * pow(GRID, 10000)
             <= pow(value, 10000) * pow(64, 9983), "actual-exponent integer-power control")
    return {"schema": "bit-moment-discharge-finite/1", "certificate": result,
            "direct_actual_exponent_controls": len(counts), "calibration": calibration(),
            "kernel_checked": False,
            "scope": "Finite exact arithmetic and source-to-Lean binding only; explicit kernel mode builds the Real theorem."}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
