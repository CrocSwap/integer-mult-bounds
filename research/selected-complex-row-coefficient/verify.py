#!/usr/bin/env python3
"""The complex row coefficient c_row of the #4470 outer-reserve constant is one.

Checks the chain of custody for the complex row reservation, then reruns the
pinned lockstep-live-role-audit computation of C with c_row = 1 in place of
the assumed 2^64. The pinned script is not modified on disk: its bytes are
authenticated, exactly two assumption lines are substituted in memory, and the
result is compared with the original run. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import json
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "selected-complex-row-coefficient"
CONSTANT_C = ROOT / "research/lockstep-live-role-audit/constant_c.py"

PHRASES = (
    ("notes/batched-complex-rows.tex", " k_0=D_{\\rm c}(d),\\qquad"),
    ("notes/batched-complex-rows.tex", " q_0=\\lceil\\log_2 W\\rceil\\,k_0,"),
    ("notes/batched-complex-rows.tex", "chunks; neither compact field is included in it.  Pad its count to the"),
    ("notes/batched-complex-rows.tex", "$1/W$ of its parent's volume, with enough row divisibility for its"),
    ("research/kappa-rebuild/transfer-audit/AUDIT.md", "The row stock is based on B, not B+O. Its reserved-axis coefficient may be"),
    ("research/kappa-rebuild/transfer-audit/AUDIT.md", "`ceil(log2 B)*log_N(d)=O(log d)`. The new child ratio is `1/N`, with a strict"),
    ("research/kappa-rebuild/transfer-audit/AUDIT.md", "\\[\nA(e)\\le A(f)+Pf+E,\\qquad f=\\lfloor e/N\\rfloor.\n\\]"),
    ("research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md",
     "Induction removes all recursive calls: the only remaining paid children"),
    ("research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md", "reserved complete chunks. This bound retains the **product** of stock"),
    ("research/lockstep-live-role-audit/constant_c.py",
     "    # AUDIT s6: complex row stock proportional to ceil(log2 B_c) * log_{N_c}(d);"),
    ("research/lockstep-live-role-audit/README.md", "1. Derive the two inherited coefficients of `C` (`c_row <= 2^64`,"),
)

ASSUMED_ROW = "    log2_c_row = 64\n"
DERIVED_ROW = "    log2_c_row = 0\n"
ORIGINAL = {"log2_C_upper": 64215200000088, "complex_share_log2": 64215200000086, "fit_log2p": 64473100659114}
DERIVED = {"log2_C_upper": 64215200000024, "complex_share_log2": 64215200000022, "fit_log2p": 64473100659050}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"] for row in sources["files"]}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        need(digest == row["sha256"], "pin " + row["path"])
    for path, phrase in PHRASES:
        need(path in pinned, "unpinned phrase source " + path)
        need(phrase in (ROOT / path).read_text(encoding="utf-8"), f"phrase in {path}: {phrase[:60]}")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def depth(d: int, n: int) -> int:
    """Outer complex recursion: rank-one paid children are jobs of size floor(d/N)."""
    k = 0
    while d >= n:
        d //= n
        k += 1
    return k


def depth_lemma() -> None:
    # D_c(d) = floor(log_N d) <= log_N d, so q_0 = ceil(log2 W) D_c(d) <= ceil(log2 W) log_N d: c_row = 1.
    for n in (2, 3, 7, 64, 1 << 20):
        for d in list(range(1, 5000)) + [n**j + s for j in range(1, 6) for s in (-1, 0, 1)]:
            k = depth(d, n)
            need(n**k <= d < n ** (k + 1) or (k == 0 and d < n), f"depth is floor(log_N d) at N={n}, d={d}")


def rerun_constant(source: str, label: str) -> dict:
    module = types.ModuleType("lockstep_constant_c_" + label)
    module.__file__ = str(CONSTANT_C)
    exec(compile(source, str(CONSTANT_C), "exec"), module.__dict__)
    return module.compute()


def recompute() -> None:
    source = CONSTANT_C.read_text(encoding="utf-8")
    need(source.count(ASSUMED_ROW) == 1, "assumed c_row line is unique")
    original = rerun_constant(source, "original")
    for key, value in ORIGINAL.items():
        need(original[key] == value, f"original {key}")
    derived = rerun_constant(source.replace(ASSUMED_ROW, DERIVED_ROW), "derived")
    for key, value in DERIVED.items():
        need(derived[key] == value, f"derived {key}")
    need(original["log2_C_upper"] - derived["log2_C_upper"] == 64, "c_row = 1 removes 64 bits from log2 C")
    lower = derived["complex_share_lower_log2_same_realization"]
    need(derived["complex_share_log2"] - lower == 68, "upper and lower complex shares now differ by 68 bits")
    # The old-supplier term log2 A_old + 10 never binds: the complex share dominates.
    need(derived["log2_C_upper"] > 64 + 10 + 10**13, "A_old term is not binding")


def main() -> None:
    pins_and_phrases()
    depth_lemma()
    recompute()
    print("PASS_SELECTED_COMPLEX_ROW_COEFFICIENT c_row=1 log2_C<=64215200000024 "
          "fit_log2p=64473100659050 no_new_kappa")


if __name__ == "__main__":
    main()
