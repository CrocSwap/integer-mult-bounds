#!/usr/bin/env python3
"""Where the next gain is on this word, modelled exactly.

The bit branch's coarse saving is the largest `a` on the 10^-18 grid whose paid
moment is below 1:

    sum_r n_r * r/(W*m) * exp(a*ln(m/r))  +  BAD * 32 m^2 * edges/(W*m) * exp(a*ln m) < 1,

with `m*W - sum n_r r = D` the row identity. The moment increases in `a`, so two
words with the same `D` differ only through the child ledger.

PR197 lowered a word's ledger by *banking* the rank-60 exterior corrections: the
rank-60 children, one per selected gauge, are replaced by shared banks, so those
entries leave the ledger and the stock falls to what the identity still requires.
This script models that transformation exactly -- drop the rank-60 entries, keep
`D`, set `W = (mass + D)/m` -- checks the model against the three published values
it can be checked on, and then applies it to this package's bit word.

Everything is exact rational arithmetic, on the enclosure implementation of the
supplier whose certificate is being reproduced (`references/pr200/interval_moment.py`,
the arithmetic PR200's own `bit/prove.py` prices with). The reported grid points
are therefore identical on every platform, and the three checks are *exact*
reproductions rather than tolerances. Rows are taken over the family's three
copies so that the stock stays integral, which leaves the saving unchanged.

The transformation is accounting, validated on another word of the same family. On
PR200's word it is a *prediction*: the bank construction is not built here.

    python3 -B levers.py [--out levers.json]
"""
import argparse
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
COPIES = 3
RANK60 = 60
GRID = 10 ** 18
BAD = Q(1, 10 ** 16)
CLAIM = Q(1693287, 2500000000)

# Published values the model is checked against, exactly.
PR187_COARSE = Q(167724995262213, 250000000000000000)
PR187_PACKED = Q(676537710350481, GRID)         # PR197's certified banked word
PR200_COARSE = Q(677773948354561, GRID)         # PR200's certified bit word


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def three_copies(profile):
    """The family's three-copy row: integral stock, same saving as one copy."""
    m = int(profile["m"])
    W = Q(profile["W_per_vertex"] if "W_per_vertex" in profile else profile["W"])
    D = Q(profile["deficit_per_vertex"] if "deficit_per_vertex" in profile else profile["N"])
    key = "child_multiplicities" if "child_multiplicities" in profile else "child_histogram"
    hist = {int(r): COPIES * int(n) for r, n in profile[key].items() if n}
    mass = sum(r * n for r, n in hist.items())
    D, W = D * COPIES, W * COPIES
    assert m * W - mass == D, "row identity"
    assert W.denominator == 1, "three-copy stock must be integral"
    return row(m, int(W), D, hist)


def row(m, W, D, hist):
    return dict(m=m, W=W, N=D, L=0, total_rank=sum(r * n for r, n in hist.items()),
                maxchild=max(hist), child_multiplicities=dict(sorted(hist.items())))


def paid_moment(interval, profile, a):
    """PR200's `bit/prove.py` price: the child ledger plus the rare-class fallback."""
    raw = interval.moment(profile, a)
    m, W = profile["m"], profile["W"]
    edges = sum(profile["child_multiplicities"].values())
    low, high = interval.log_interval(Q(m))
    exp_low, exp_high = interval.exp_interval(a * low, a * high)
    weight = BAD * Q(32 * m * m * edges, W * m)
    return dict(upper=raw["upper"] + weight * exp_high,
                lower=raw["lower"] + weight * exp_low)


def certified(interval, profile):
    """The largest 10^-18 grid point that pays, as PR200's own `certify` finds it."""
    low, high = 0, GRID // 100
    assert paid_moment(interval, profile, Q(low, GRID))["upper"] < 1, "zero-saving contraction"
    assert paid_moment(interval, profile, Q(high, GRID))["lower"] > 1, "upper bracket"
    while high - low > 1:
        mid = (low + high) // 2
        if paid_moment(interval, profile, Q(mid, GRID))["upper"] < 1:
            low = mid
        else:
            high = mid
    accepted = paid_moment(interval, profile, Q(low, GRID))["upper"]
    rejected = paid_moment(interval, profile, Q(high, GRID))["lower"]
    assert accepted < 1 < rejected, "adjacent grid exclusion"
    return Q(low, GRID)


def banked(profile):
    """PR197's accounting: the rank-60 exterior corrections become banked roles."""
    hist = profile["child_multiplicities"]
    assert hist.get(RANK60), "no rank-60 exterior corrections to bank"
    trimmed = {r: n for r, n in hist.items() if r != RANK60}
    mass = sum(r * n for r, n in trimmed.items())
    packed = row(profile["m"], (mass + profile["N"]) // profile["m"], profile["N"], trimmed)
    assert packed["W"] * packed["m"] - mass == packed["N"], "banked row identity"
    assert packed["W"] < profile["W"], "the stock must fall"
    return packed


def check(interval, name, profile, published):
    model = certified(interval, profile)
    assert model == published, (name, str(model), str(published))
    return dict(name=name, published=str(published), published_decimal=float(published),
                model=str(model), model_decimal=float(model),
                W=profile["W"], deficit=str(profile["N"]),
                maxchild=profile["maxchild"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "levers.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    interval = module("levers_interval_moment", HERE / "references/pr200/interval_moment.py")

    validations = []
    pr187 = three_copies(json.loads((HERE / "references/pr187/certificate.json").read_text())["profile"])
    validations.append(check(interval, "PR187 unpacked row", pr187, PR187_COARSE))
    validations.append(check(interval, "PR187 banked row (PR197)", banked(pr187), PR187_PACKED))

    bit = json.loads((HERE / "inputs/pr200-bit-certificate.json").read_text())["bit"]["profile"]
    per_copy = {int(r): int(n) for r, n in bit["child_histogram"].items() if n}
    pr200 = three_copies(bit)
    validations.append(check(interval, "PR200 unpacked row", pr200, PR200_COARSE))

    packed = banked(pr200)
    packed_saving = certified(interval, packed)
    now = Q(validations[-1]["model"])
    ceiling_now, ceiling_packed = now / (1 + now), packed_saving / (1 + packed_saving)
    gain = ceiling_packed / CLAIM - 1
    for v in validations:
        print("[validated] {name}: model {model} = published {published} exactly "
              "(W={W}, N={deficit}, maxchild={maxchild})".format(**v))
    print("[PR200 now]     coarse {} ({:.10g}) -> ceiling {:.10g}".format(
        now, float(now), float(ceiling_now)))
    print("[PR200 banked]  W={} (= {:d}/3 per vertex) -> coarse {} ({:.10g}) -> "
          "ceiling {:.10g}".format(packed["W"], 3 * packed["W"], packed_saving,
                                   float(packed_saving), float(ceiling_packed)))
    print("[lever]         banking the rank-60 exterior corrections is worth {:.4f}% of "
          "kappa ({:.10g} -> {:.10g})".format(float(ceiling_packed / ceiling_now - 1) * 100,
                                              float(ceiling_now), float(ceiling_packed)))
    print("[vs the claim]  {} ({:.10g}) -> {:.4f}%".format(
        CLAIM, float(CLAIM), float(gain) * 100))

    out = dict(
        status="MODELLED, NOT CONSTRUCTED: the banked row is validated against PR197's "
               "certified word, but the bank construction on PR200's word is not built here "
               "and no claim is made about it.",
        method="PR200's exact interval arithmetic on the 10^-18 grid, three-copy rows; the "
               "three published values are reproduced exactly, not to a tolerance",
        copies=COPIES,
        validations=validations,
        pr200_unpacked=dict(coarse=str(now), coarse_decimal=float(now),
                            ceiling=str(ceiling_now), ceiling_decimal=float(ceiling_now)),
        pr200_banked=dict(W_three_copies=packed["W"],
                          W_per_vertex=str(Q(packed["W"], COPIES)),
                          W_per_vertex_decimal=float(Q(packed["W"], COPIES)),
                          coarse=str(packed_saving), coarse_decimal=float(packed_saving),
                          ceiling=str(ceiling_packed), ceiling_decimal=float(ceiling_packed),
                          rank60_children_per_copy=per_copy[RANK60],
                          rank60_mass_per_copy=RANK60 * per_copy[RANK60],
                          ledger_share_of_rank60=float(
                              Q(RANK60 * per_copy[RANK60],
                                sum(r * n for r, n in per_copy.items()))),
                          deficit_three_copies=str(pr200["N"])),
        claim=dict(kappa=str(CLAIM), kappa_decimal=float(CLAIM)),
        gain_vs_claim=float(gain),
    )
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("[write] " + str(args.out))


if __name__ == "__main__":
    main()
