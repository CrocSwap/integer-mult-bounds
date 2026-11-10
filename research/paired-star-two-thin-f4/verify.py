#!/usr/bin/env python3
"""F_4 two-thin census on the g=3, d=2 paired-star full-call contract.

The star matrix and the commuting control maps are checked here. The census is
the compiled search. Failures are raised, so python -O still fails closed.
class_cap=184 is an unfinished search: PASS records that split and does not
treat those classes as rank-sum proofs.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
BINARY = Path("/tmp/paired-star-two-thin-f4")

STAR = (0x54, 0xA8, 0x01, 0x02, 0x01, 0x02, 0x01, 0x02)
F4_MUL = (
    (0, 0, 0, 0),
    (0, 1, 2, 3),
    (0, 2, 3, 1),
    (0, 3, 1, 2),
)
F4_INV = (0, 1, 3, 2)


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def rank_f2(rows):
    work = list(rows)
    rank = 0
    for col in range(8):
        mask = 1 << col
        pivot = next((i for i in range(rank, 8) if work[i] & mask), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(8):
            if i != rank and (work[i] & mask):
                work[i] ^= work[rank]
        rank += 1
    return rank


def mul_f2(left, right):
    out = []
    for row in left:
        acc = 0
        bit = 0
        rest = row
        while rest:
            if rest & 1:
                acc ^= right[bit]
            rest >>= 1
            bit += 1
        out.append(acc)
    return tuple(out)


def control_maps():
    thin0 = [0] * 8
    thin1 = [0] * 8
    for leaf in (1, 2):
        for bit in range(2):
            thin0[bit] |= 1 << (2 * leaf + bit)
            thin0[2 * leaf + bit] |= 1 << bit
    for bit in range(2):
        thin1[bit] |= 1 << (6 + bit)
        thin1[6 + bit] |= 1 << bit
    return tuple(thin0), tuple(thin1)


def check_star():
    require(F4_MUL[2][2] == 3 and F4_MUL[2][3] == 1 and F4_MUL[3][3] == 2, "F4 product")
    for value in (1, 2, 3):
        require(F4_MUL[value][F4_INV[value]] == 1, "F4 inverse")
    thin0, thin1 = control_maps()
    difference = tuple(a ^ b for a, b in zip(thin0, thin1))
    require(difference == STAR, "control maps differ by the star")
    require(rank_f2(thin0) == 4 and rank_f2(thin1) == 4 and rank_f2(STAR) == 4, "control ranks")
    square = mul_f2(STAR, STAR)
    require(square != STAR and any(square), "star square")
    require(mul_f2(square, STAR) == STAR, "star cube")


def run(argv):
    proc = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(
            "FAIL: "
            + " ".join(argv)
            + "\n"
            + proc.stdout
            + proc.stderr
        )
    return proc.stdout


def fields(text):
    found = {}
    for token in text.split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        found[key] = value
    return found


def check_search():
    compiled = subprocess.run(
        ["gcc", "-O3", "-std=c11", "-fopenmp", "-o", str(BINARY), str(PKG / "search.c")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    require(compiled.returncode == 0, "gcc\n" + compiled.stderr)
    control_text = run([str(BINARY), "control"])
    control = fields(control_text)
    require("PASS_CONTROL" in control_text, "control token")
    require(control.get("control_nullity") == "16", "control nullity")
    require(control.get("control_f4_min") == "8", "control F4 minimum")
    require(control.get("control_nodes") == "454928", "control nodes")
    audit_text = run([str(BINARY), "audit", "11"])
    audit = fields(audit_text)
    require("PASS_AUDIT" in audit_text, "audit token")
    require(audit.get("audit_eval_target_mismatch") == "0", "target evaluation")
    require(audit.get("poly_hits") == "159984", "polynomial hits")
    require(audit.get("spec_hits") == "159984", "specialization hits")
    require(audit.get("eval_hits") == "159984", "evaluation hits")
    require(audit.get("disagree") == "0", "scalar disagreement")
    require(audit.get("overflow") == "0", "audit overflow")
    census_text = run([str(BINARY), "census", "0", "11"])
    require("PASS_CENSUS" in census_text, "census token")
    census = fields(census_text)
    expected = {
        "screened": "1244160",
        "exact_hits": "159984",
        "consistent": "566352",
        "inconsistent": "2793312",
        "signatures": "1746",
        "class_ge8": "1562",
        "class_low": "0",
        "class_cap": "184",
        "class_bad": "0",
        "min_nullity": "7",
        "max_nullity": "32",
        "dep_bad": "0",
        "crank_bad": "0",
        "diff_bad": "0",
        "affine_bad": "0",
    }
    for key, value in expected.items():
        require(census.get(key) == value, key + " was " + str(census.get(key)))
    require("LOW " not in census_text, "low-rank witness")
    print("proved_f4_classes=1562 unresolved_f4_classes=184")
    print("PASS_PAIRED_STAR_TWO_THIN_F4")


def main():
    check_star()
    check_search()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("FAIL: " + str(exc) + "\n")
        sys.exit(1)
