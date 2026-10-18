#!/usr/bin/env python3
"""Exact checks for research/selected-stock-envelope-m73 (card selected-stock-envelope).

Scope: the selected m=73 complex stopped producer's stock quantities at one
bootstrap stage, and the exact missing shape lemma that blocks its uniform
stock coefficient. Exact integer arithmetic only; no repository code is
imported or executed. Aaron Wang, with help from opencode. Apache-2.0.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# sha256 of every pinned input, byte-bound to base commit 18aacb215fc3717b06be8ceb9fca62aeca0d3e99
PINNED = {
    "research/selected-coarse-depth-stock/PROOF.md":
        "fe1a29b3757a3fda7124027e7e14228a6f3aa49521e23822909036172807f800",
    "research/selected-coarse-depth-stock/README.md":
        "17e178968eeb8bb7905df601a6c95c9b5491fd94c4cd6516802f00dc4abe03a1",
    "notes/three-stage-cover-bit.tex":
        "47123a756f823c83a0d48cca2bf5add6472cd88410b13aed345e70c8834fb511",
    "notes/three-stage-cover-complex.tex":
        "1c5b638aa9b75365b8addec9c8eeee6bc5e499722901079b94c65fce033fde8a",
    "docs/research/selected-bootstrap-scope-map.md":
        "b9196c339ed06c749780749d30c93f2deba0ebb489368a1eb4505e461a1c3062",
    "research/community-frontier1094-audit/ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}

failures = []
checks = 0


def require(cond, label):
    global checks
    checks += 1
    if not cond:
        failures.append(label)


def read(rel):
    with open(os.path.join(ROOT, rel.replace("/", os.sep)), "rb") as fh:
        return fh.read()


def text(rel):
    return read(rel).decode("utf-8")


def sp_order(n):
    """|Sp(2n, 2)| = 2^(n^2) * prod_{j=1..n} (2^(2j) - 1)."""
    val = 2 ** (n * n)
    for j in range(1, n + 1):
        val *= 2 ** (2 * j) - 1
    return val


def main():
    # 0. Byte-pinned inputs.
    for rel, digest in PINNED.items():
        require(hashlib.sha256(read(rel)).hexdigest() == digest, "pin:" + rel)

    proof = text("research/selected-coarse-depth-stock/PROOF.md")
    creview = text("research/selected-coarse-depth-stock/README.md")
    cover_bit = text("notes/three-stage-cover-bit.tex")
    cover_cx = text("notes/three-stage-cover-complex.tex")
    scope_map = text("docs/research/selected-bootstrap-scope-map.md")
    assembly = json.loads(text("research/community-frontier1094-audit/ASSEMBLY.json"))

    # 1. Exact symplectic order and the 2,642-bit per-level stock allowance B.
    order = sp_order(36)              # |Sp(72, 2)| = |O(73, 2)|
    require(order.bit_length() == 2628, "sp72 order bit length 2628")
    families = 14336 + 480 + 8 + 2    # data/owner, helpers, private centres, coefficient work
    require(families == 14826, "physical family decomposition")
    require(families.bit_length() == 14, "family bit length 14")
    require(order.bit_length() + families.bit_length() == 2642,
            "B = 2628 + 14 = 2642")
    require((order * families).bit_length() <= 2642, "product fits 2642 bits")
    require(2 ** 2627 <= order < 2 ** 2628, "order magnitude band")

    # 2. Halving guard of the m=73 complex producer (max child rank 48).
    require(73 * 73 == 5329, "73 squared")
    require(2 * 48 * 48 == 4608, "2*48 squared")
    require(73 * 73 > 2 * 48 * 48, "two levels more than halve")

    # 3. Retained row ledgers, recomputed.
    B = 2642
    require(2 * B + 9909 + 252 + 1024 == 16469, "retained ledger 16469")
    require(16469 < 20161, "row guard cap")
    refined = -((-43 * B) // 26)      # ceil(43*B/26)
    require(refined == 4370, "refined per-log charge 4370")
    require(refined + 9909 + 252 + 1024 == 15555, "conditional ledger 15555")
    require(16469 - 15555 == 914, "reduction 914")

    # 4. Source-bound citations (substring checks on the pinned bytes).
    require("Actual A, B and rho are **not established here**" in proof,
            "cite: missing A B rho")
    require("sigma <= (43/26)*(1-s)*(A+B) + rho" in proof, "cite: composition")
    require("2*B + 9909 + 252 + 1024 = 16469 < 20161" in proof, "cite: ledger")
    require("4370 + 9909 + 252 + 1024 = 15555" in proof, "cite: refined ledger")
    require("14,336 data/owner, 480" in proof, "cite: family split")
    require("16469 -> 15555" in creview, "cite: README reduction")
    require("W_0q^{m^2(w-1)}" in cover_bit, "cite: ordinary w-shaped cover")
    require("charged in the row reserve" in cover_bit, "cite: row reserve digits")
    require("finite orthogonal cover" in cover_cx, "cite: complex cover heading")
    require("The selected complex supplier has `m=73` and binds the shared saving"
            in scope_map, "cite: m=73 binding")
    require("PR589 BIT `m=64`" in scope_map, "cite: ordinary producer m=64")
    require("do not identify fourteen" in scope_map,
            "cite: headroom vs envelope")
    require(assembly["bootstrap"][0]["cutoff_log2"] == "4785575287428",
            "stage-1 cutoff")
    require(assembly["binding"] == "complex", "binding complex")

    # 5. The exact obstruction: no w-shaped per-level divisor in the complex
    #    cover note (bounded no-match over the pinned file).
    require("q^{m^2(w-1)}" not in cover_cx, "no w-shaped divisor in complex cover")
    require("W(w)" not in cover_cx, "no W(w) in complex cover")
    require("W(w)=W_0q^{m^2(w-1)}" in cover_bit.replace(" ", ""),
            "ordinary cover carries W(w)")

    # 6. Sufficient-guard comparison (consistency only, not the contribution):
    #    ceil(log2(8*sigma)) for the two conditional ledger coefficients.
    def guard(sigma):
        return (8 * sigma - 1).bit_length()

    require(guard(16469) == 18, "guard 18 at 16469")
    require(guard(15555) == 17, "guard 17 at 15555")
    H1 = 6562783  # research/selected-bootstrap-stock-audit/README.md (both branches)
    require(18 <= H1, "stage-1 sufficient guard passes")

    # 7. Mutation controls: each must be rejected by its check.
    require(sp_order(35).bit_length() != 2628, "control: Sp(70,2) rejected")
    require(2 * B + 9909 + 252 + 1024 != 16468, "control: ledger off-by-one rejected")
    require(-((-43 * (B + 1)) // 26) != 4370, "control: wrong B rejected")
    require(not (73 * 73 > 2 * 52 * 52), "control: rank-52 halving rejected")
    require("W(w)=W_0q^{m^2(w-2)}" not in cover_bit.replace(" ", ""),
            "control: wrong cover exponent rejected")

    if failures:
        for f in failures:
            print("FAIL", f)
        return 1
    print("PASS_SELECTED_STOCK_ENVELOPE_M73 "
          "sp72_bits=2628 families=14826 B=2642 ledger=16469->15555 "
          "halving=5329>4608 guard=18,17<=6562783 "
          "missing_lemma=A_B_rho_unbound controls=5 checks=%d" % checks)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
