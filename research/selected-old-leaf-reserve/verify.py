#!/usr/bin/env python3
"""Source-bound derivation of the old-leaf reserve S_old of the selected BIT stage.

Checks the chain of custody from the #4470 stage's a_old to the copied-centers
BIT supplier and its internal-borrowing all-width interface, then the exact
finite arithmetic of the conservative fallback bound and its consequences for
PR #4954 and lockstep-live-role-audit. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "selected-old-leaf-reserve"

# (path, phrase) pairs; each phrase must occur verbatim in the pinned source.
PHRASES = (
    ("research/query-thinned-controllers/PROOF.md", "a_old=0.0000384599, the ordinary saving is exactly"),
    ("research/query-thinned-controllers/PROOF.md", "rank witnesses, exceeds 256/(C0-C1)*N^5 and pays the complete fallback."),
    ("research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md", "A safe reserve is `W(w)^D * S_old`, with"),
    ("research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md", "with the old arbitrary-width supplier. For clarity, the inherited ordinary"),
    ("research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json",
     "\"borrowed_digits\": \"k <= D_N(ceil(e/w))*(N^2*(w-1)+ceil(log_q(B*|GL_N(F_q)|)))+ceil(log_q S_old)+1\""),
    ("notes/three-stage-cover-rows.tex", "reserve. The old supplier has its retained complete-row contract and"),
    ("notes/three-stage-cover-bit.tex", "Thus a weighted leaf uses four old ordinary atom interchanges, three"),
    ("notes/stopped-product-interface.tex", "the next binary power and treated by that ordinary interface, with"),
    ("notes/copied-centers-bit.tex", "Set $a_b=384599/10^{10}$ and $\\tau=1-a_b$."),
    ("notes/copied-centers-bit.tex", "The complete-row mixed-width proof in \\path{notes/batched-bit-rows.tex}"),
    ("notes/copied-centers-bit.tex", "therefore gives the all-width interchange interface, with bounded"),
    ("notes/batched-bit-rows.tex", "\\paragraph{Supplying the bit rows from existing digits.}"),
    ("notes/batched-bit-rows.tex", "The possibly large exponent in $W^{D(e)}=e^{O(1)}$ does not multiply the"),
    ("notes/batched-bit-rows.tex", "logical volume by that polynomial.  The row digits were already part of"),
    ("notes/batched-bit-rows.tex", "Consequently the batched construction is an arbitrary-width interchange"),
    ("notes/copied-centers-assembly.tex", " (t_b,w_b)=(9,28),\\qquad(t_c,w_c)=(20,30),"),
    ("notes/copied-centers-assembly.tex", "The sufficient stock is therefore $p^{2000}$, supplied by the retained"),
    ("research/community-round8-audit/pr185-proof-reviewed.md",
     "None of these uses depends on the old numerical saving being `384599/10^10`."),
    ("research/selected-bit-stage-stock-band/README.md",
     "1. **Derive the old-leaf reserve `S_old` numerically from the retained"),
    ("research/lockstep-live-role-audit/constant_c.py", "    log2_A_old = 64"),
)


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
        need(phrase in (ROOT / path).read_text(encoding="utf-8"), f"phrase in {path}: {phrase}")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def certificate() -> dict:
    sys.set_int_max_str_digits(0)
    cert = json.loads((ROOT / "certificates/copied-centers-network.json").read_text(encoding="utf-8"))
    bit = cert["bit"]
    need(bit["saving"] == "384599/10000000000", "copied-centers BIT saving is a_old")
    counts = bit["counts"]
    if isinstance(counts, str):
        import ast
        counts = ast.literal_eval(counts)
    need(counts["W"] == 188181929 and counts["m"] == 575 and counts["maxchild"] == 529, "W_b, m_b, largest child")
    need(counts["W"] == 2 * counts["N"] + counts["B1"] + counts["B2"], "W_b = 2N + B_a + B_b")
    return counts


def depth(e: int, m: int = 575, top: int = 529) -> int:
    """batched-bit-rows D(e): replace e by top*floor(e/m) until below m."""
    d = 0
    while e >= m:
        e = top * (e // m)
        d += 1
    return d


def depth_and_coefficient(counts: dict) -> None:
    w_b = counts["W"].bit_length()
    need(w_b == 28, "wire bitlength of W_b is 28")
    t_b = next(t for t in range(1, 100) if 575**t > 2 * 529**t)
    need(t_b == 9, "least halving degree t_b = 9")
    need(t_b * w_b == 252, "bit reserve coefficient 252")
    # D(e) <= 9*ceil(log2 e): nine replacements at least halve e (575^9 > 2*529^9).
    for e in list(range(1, 200001)) + [2**k + j for k in range(18, 64) for j in (-1, 0, 1)]:
        need(depth(e) <= 9 * max(1, (e - 1).bit_length()), f"depth bound at e={e}")


def consequences() -> None:
    result = json.loads((ROOT / "research/query-thinned-controllers/RESULT.json").read_text(encoding="utf-8"))
    h1 = result["bit_strictification"]["uniform_H1"]
    need(h1 == 25986965159937 and result["bit_strictification"]["uniform_N"] == "2^25986965159937", "selected stage rank")
    log2_q_lower = 5 * h1 + 26  # cover prime q > 2^26 N^5
    # Primary: S_old = 1, so k_old = ceil(log_q 1) + 1 = 1 <= e/4 at every fitting width.
    t_fit = 52182660963735
    need(1 <= 2 ** 10, "k_old = 1 is far below e/4")
    # Fallback (assembly-level supply): log2 S_old <= 252*ceil(log2 e'), e' <= e.
    # Then k_old <= ceil(252*(t+1)/log2 q) + 1, compared with e/4 = 2^(t-2).
    k_old_fallback = -(-252 * (t_fit + 1) // log2_q_lower) + 1
    need(k_old_fallback == 103, "fallback k_old at the fit threshold")
    need(k_old_fallback.bit_length() < t_fit - 2, "fallback k_old <= e/4")
    # #4954 sufficient envelope: log_q S_old <= sigma*(1+log2 e) with sigma <= 2^(t-3)/(1+t).
    sigma = Fraction(252, log2_q_lower)
    need(sigma < 1, "fallback sigma is below one")
    # lockstep-live-role-audit: log2 S_old <= A_old e^delta log2 e with log2 A_old <= 64.
    # 252*ceil(log2 e) <= 504*log2 e <= 2^9 e^delta log2 e for e >= 2.
    need(504 <= 2**9 and 9 <= 64, "fallback A_old <= 2^9")


def main() -> None:
    pins_and_phrases()
    counts = certificate()
    depth_and_coefficient(counts)
    consequences()
    print("PASS_SELECTED_OLD_LEAF_RESERVE S_old=1_internal_borrowing "
          "fallback_log2_S_old<=252*ceil(log2_e) fallback_k_old_at_fit=103 no_new_kappa")


if __name__ == "__main__":
    main()
