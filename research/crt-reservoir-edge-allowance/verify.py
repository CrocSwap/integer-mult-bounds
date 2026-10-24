#!/usr/bin/env python3
"""Edge ratio 12 against the printed coefficient p/6400.

The layout is the power-of-two edge from the production-ratio package.
The comparison is one integer division. No schedule is replayed, and no
new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-edge-allowance"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

PRODUCT = "r (2/B + β) E ≤ (C_E p / 6400) 2^{−60 ell} (p+2)^{−48}."


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    proof = (ROOT / "research/compact-switch-sharp-density/PROOF.md").read_text(encoding="utf-8")
    need(PRODUCT in proof, "printed product line")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def edge(allocator) -> None:
    modulus = (1 << 24) - 2
    layout = allocator.Layout(modulus, 24, (23,) * 65536)
    need(layout.p == 16777214 and layout.ell == 24 and layout.G == 3072, "edge parameters")
    need(layout.r_max == 4 and layout.L == 1507328 and layout.L <= layout.p, "edge length")
    need(layout.p + 2 == 1 << 24, "no envelope slack")
    need(3 * layout.r_max == 12, "edge ratio equals 12")
    threshold = 12 * 6400
    need(threshold == 76800 and threshold < layout.p, "12 * 6400 is strictly below p")
    quotient, remainder = divmod(layout.p, threshold)
    need(quotient == 218 and remainder == 34814, "p / (12 * 6400) lies in (218, 219)")
    gap, gap_remainder = divmod(layout.p - threshold, 6400)
    need(gap == 2609 and gap_remainder == 2814, "p/6400 - 12 = 2609 + 2814/6400")


def main() -> None:
    pins_and_phrases()
    edge(load_allocator())
    print(
        "PASS_CRT_RESERVOIR_EDGE_ALLOWANCE "
        "threshold=76800 quotient=218 remainder=34814"
    )


if __name__ == "__main__":
    main()
