#!/usr/bin/env python3
"""Compare one #4174 production plan's address length with its p.

PR #4328 absorbs the sparse repair when L <= p. PR #4646 reuses that
hypothesis for the constant 1/6400. This verifier reads the production
layout from PR #4174 and one plan, then one other layout the same
constructor accepts. It does not rerun the descriptor census, and it
claims no new kappa.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-length-hypothesis"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"
RESULT = ROOT / "research/crt-reservoir-placement/RESULT.json"

PRODUCTION_PHRASE = "`p=9240576`, `L=1540096`, `G=3072`, `r_max=5`, `H=15360`"
HYPOTHESIS_PHRASE = "for `L ≤ p` and"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    placement = (ROOT / "research/crt-reservoir-placement/README.md").read_text(encoding="utf-8")
    tariff = (ROOT / "research/pr4100-crt-repair-tariff/README.md").read_text(encoding="utf-8")
    need(PRODUCTION_PHRASE in placement, "production constants")
    need(HYPOTHESIS_PHRASE in tariff, "L <= p hypothesis")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def production_plan(allocator) -> None:
    recorded = json.loads(RESULT.read_text(encoding="utf-8"))["production"]
    d, ell = 65536, 24
    widths = tuple(ell - (i % 2) for i in range(d))
    length = sum(widths)
    layout = allocator.Layout(6 * length, ell, widths)
    plan = next(allocator.iter_plans(layout, level=1))
    need(layout.L == length == 1540096, "production address length")
    need(layout.p == 6 * length == 9240576, "production p is six times L")
    need(layout.L <= layout.p, "production plan satisfies L <= p")
    need(layout.G == 3072 and layout.r_max == 5 and layout.H == 15360, "production guard constants")
    need(plan.level == 1 and plan.partition == 0 and plan.batch_index == 0, "first plan index")
    need(plan.active_axes == (1, 3, 5, 7, 9), "first plan axes")
    need(plan.placement.length == layout.L, "plan address length is L")
    need(layout.r_max * 19200 <= layout.p, "production r_max is at most p/19200")
    for key in ("d", "ell", "p", "L", "G", "r_max", "H"):
        need(recorded[key] == getattr(layout, key), "recorded " + key)


def longer_address(allocator) -> None:
    """The constructor does not require L <= p."""
    layout = allocator.Layout(2, 2, (1,) * 65536)
    need(layout.p == 2 and layout.L == 65536 and layout.G == 256, "longer layout constants")
    need(layout.r_max == 2, "longer layout batch size")
    need(layout.L > layout.p, "admitted layout has L > p")
    need(layout.r_max * 19200 > layout.p, "r_max exceeds p/19200")


def main() -> None:
    pins_and_phrases()
    allocator = load_allocator()
    production_plan(allocator)
    longer_address(allocator)
    print(
        "PASS_CRT_RESERVOIR_LENGTH_HYPOTHESIS "
        "production_L=1540096 production_p=9240576 longer_L=65536 longer_p=2"
    )


if __name__ == "__main__":
    main()
