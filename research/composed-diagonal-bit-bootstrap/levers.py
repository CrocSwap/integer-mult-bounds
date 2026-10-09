#!/usr/bin/env python3
"""Where the next gain is on this word, modelled exactly.

The bit branch's coarse saving is the largest `a` whose paid moment is below 1:

    sum_r n_r * r * (m/r)^a  +  BAD * 32 m^2 * edges * m^a  <  W * m,

with `m*W - sum n_r r = D` the row identity. Because the moment is increasing in
`a`, two words with the same `D` differ only through the child ledger.

PR197 lowered a word's ledger by *banking* the rank-60 exterior corrections: the
2,200 rank-60 children (one per selected gauge) are replaced by shared banks, so
the rank-60 entries leave the ledger and the stock falls to what the identity
requires. This script models that transformation exactly -- drop the rank-60
entries, keep `D`, set `W = (mass + D)/m` -- and validates the model against the
three published values it can be checked on, then applies it to this package's
bit word.

The model is accounting, validated on another word of the same family. On PR200's
word it is a *prediction*: realizing it needs the bank construction itself, which
this package does not build.

    python3 -B levers.py [--out levers.json]
"""
import argparse
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAD = Q(1, 10 ** 16)
RANK60 = 60
CLAIM = Q(1693287, 2500000000)
GRID = 10 ** 10

# Published values the model is checked against.
PR187_COARSE = Q(167724995262213, 250000000000000000)
PR187_PACKED = Q(676537710350481, 10 ** 18)     # PR197's certified packed word
PR200_COARSE = Q(677773948354561, 10 ** 18)     # PR200's certified bit word
PR200_PACKED_EXCLUDED = None


def row(profile):
    m = int(profile["m"])
    W = Q(profile["W_per_vertex"] if "W_per_vertex" in profile else profile["W"])
    D = Q(profile["deficit_per_vertex"] if "deficit_per_vertex" in profile else profile["N"])
    key = "child_multiplicities" if "child_multiplicities" in profile else "child_histogram"
    hist = {int(r): int(n) for r, n in profile[key].items() if n}
    assert m * W - sum(r * n for r, n in hist.items()) == D, "row identity"
    return m, W, D, hist


def paid_root(m, W, D, hist):
    """The largest a with paid moment below 1, on exact rationals."""
    fallback = BAD * 32 * m * m * sum(hist.values())

    def excess(a):
        return (sum(Q(n * r) * pow(Q(m, r), a) for r, n in hist.items())
                + fallback * pow(Q(m), a))

    target = W * m
    assert excess(0) < target, "zero-saving rank contraction"
    lo, hi = Q(0), Q(1)
    assert excess(hi) > target, "upper bracket"
    for _ in range(400):
        mid = (lo + hi) / 2
        if excess(mid) < target:
            lo = mid
        else:
            hi = mid
    return lo


def banked(m, W, D, hist):
    """PR197's accounting: the rank-60 exterior corrections become banked roles."""
    assert hist.get(RANK60), "no rank-60 exterior corrections to bank"
    trimmed = {r: n for r, n in hist.items() if r != RANK60}
    mass = sum(r * n for r, n in trimmed.items())
    packed_W = (mass + D) / m
    assert packed_W < W, "the stock must fall"
    return packed_W, trimmed


def check(name, model, published):
    rel = abs(model / published - 1)
    assert rel < Q(1, 10 ** 11), (name, float(rel))
    return dict(name=name, published=str(published), published_decimal=float(published),
                model=str(model), model_decimal=float(model), relative_error=float(rel))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "levers.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"

    validations = []
    pr187 = json.loads((HERE / "references/pr187/certificate.json").read_text())
    m1, W1, D1, hist1 = row(pr187["profile"])
    a1 = paid_root(m1, W1, D1, hist1)
    validations.append(check("PR187 unpacked row", a1, PR187_COARSE))
    packed_W1, trimmed1 = banked(m1, W1, D1, hist1)
    packed_a1 = paid_root(m1, packed_W1, D1, trimmed1)
    validations.append(check("PR187 banked row (PR197)", packed_a1, PR187_PACKED))

    bit = json.loads((HERE / "inputs/pr200-bit-certificate.json").read_text())
    m2, W2, D2, hist2 = row(bit["bit"]["profile"])
    a2 = paid_root(m2, W2, D2, hist2)
    validations.append(check("PR200 unpacked row", a2, PR200_COARSE))

    packed_W2, trimmed2 = banked(m2, W2, D2, hist2)
    packed_a2 = paid_root(m2, packed_W2, D2, trimmed2)
    ceiling_now, ceiling_packed = a2 / (1 + a2), packed_a2 / (1 + packed_a2)
    grid = lambda x: Q(int(x * GRID), GRID)
    for v in validations:
        print("[validated] {name}: model {model_decimal:.15g} vs published "
              "{published_decimal:.15g} (rel {relative_error:.1e})".format(**v))
    print("[PR200 now]     coarse {:.15g} (grid {:.10g}) -> ceiling {:.10g}".format(
        float(a2), float(grid(a2)), float(ceiling_now)))
    print("[PR200 banked]  W_per_vertex {} -> coarse {:.15g} (grid {:.10g}) -> ceiling "
          "{:.10g}".format(packed_W2, float(packed_a2), float(grid(packed_a2)),
                           float(ceiling_packed)))
    print("[lever]         banking the rank-60 exterior corrections is worth {:.4f}% of "
          "kappa ({:.10g} -> {:.10g})".format(100 * (ceiling_packed / ceiling_now - 1),
                                              float(ceiling_now), float(ceiling_packed)))
    print("[vs the claim]  {} ({:.10g}) -> {:.4f}%".format(
        CLAIM, float(CLAIM), 100 * (ceiling_packed / CLAIM - 1)))

    out = dict(
        status="MODELLED, NOT CONSTRUCTED: the banked row is validated against PR197's "
               "certified word, but the bank construction on PR200's word is not built here "
               "and no claim is made about it.",
        method="paid moment < 1 solved by exact rational bisection; row identity m*W - mass = D",
        validations=validations,
        pr200_unpacked=dict(coarse=str(a2), coarse_decimal=float(a2),
                            ceiling=str(ceiling_now), ceiling_decimal=float(ceiling_now)),
        pr200_banked=dict(W_per_vertex=str(packed_W2),
                          W_per_vertex_decimal=float(packed_W2),
                          coarse=str(packed_a2), coarse_decimal=float(packed_a2),
                          coarse_grid=str(grid(packed_a2)),
                          ceiling=str(ceiling_packed), ceiling_decimal=float(ceiling_packed),
                          rank60_children=hist2[RANK60], rank60_mass=RANK60 * hist2[RANK60],
                          ledger_share_of_rank60=float(
                              Q(RANK60 * hist2[RANK60], sum(r * n for r, n in hist2.items()))),
                          deficit=str(D2)),
        claim=dict(kappa=str(CLAIM), kappa_decimal=float(CLAIM)),
        gain_vs_claim=float(ceiling_packed / CLAIM - 1),
    )
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
