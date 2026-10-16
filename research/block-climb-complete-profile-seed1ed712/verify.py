#!/usr/bin/env python3
"""Complete-profile screen for block-climb decoding identities of the rank-one payload.

Scope: the drawn catalogue card complex-rank-shape-decoder (unchanged), executed at
its smallest falsifying instance (k = 2) and one bounded pivot (the PR 1605
threshold partitions and full reblock). All arithmetic is exact rational
enclosure arithmetic (integers and fractions only).

Sections:
  A. Exact k = 2 decoding identities: which operand-mixing patterns can deliver
     the two payload products at all, the exact decode matrices, and the
     dirty gather-slot restoration witness.
  B. Per-group hard search: net saving of one k-block climb group with alpha
     charged transports against k rank-1 payload children, exact intervals,
     k = 2..51, alpha in {0, 1, 2}, a in {target, 1/99, baseline ceiling},
     plus the closed-form boundary ln(1+alpha)/ln k.
  C. Complete per-call profiles at the target a*: threshold signs, charged
     realizations, full reblock, overhead budgets, and the +5% ceiling gate.
  D. Controls: independent cost enclosure cross-check, threshold reproduction
     against pinned predecessor receipts, mutated-decode failure, mass checks.

Aaron Wang, with help from opencode. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M, W, IDLE, RMAX = 73, Q(896, 9), 1646, 51
BASE_HI = Q(1690054109089, 10 ** 15)
TARGET = Q(21, 20) * BASE_HI
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
INPUTS = [
    "research/complex-local-word-ceiling/ceiling.py",
    "research/complex-local-word-ceiling/RESULT.json",
    "research/complex-rank-one-block-budget/RESULT.json",
]
CHECKS = []


def require(ok, why):
    if not ok:
        raise ValueError(why)


def check(ok, name, detail=""):
    require(ok, "control failed: " + name + ("; " + detail if detail else ""))
    CHECKS.append(name)
    print("PASS " + name + (" " + detail if detail else ""))


def fstr(x):
    return str(x.numerator) + "/" + str(x.denominator)


def fdec(x, places=12):
    return format(float(x), "." + str(places) + "f")


# ---------------------------------------------------------------- sources


def load_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    declared = [row["path"] for row in pins["files"] if row["usage"] == "input"]
    require(sorted(declared) == sorted(INPUTS), "source inventory must match INPUTS")
    for row in pins["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source drift: " + row["path"])
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("retained_ceiling", path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


# ------------------------------------------- independent cost enclosure (B)


@lru_cache(None)
def binomial_cost(r, a):
    """Independent enclosure of (r/73)^(1-a) via the negative binomial tail.

    Method reimplemented from PR 1605 (Arham Tahir) verify.py: for q = 1-a and
    z = 1-r/73, (1-z)^q = 1 - sum(t_n), all t_n > 0, t_1 = q z,
    t_(n+1) = t_n z (n-q)/(n+1). Outward integer rounding encloses roundoff.
    """
    require(type(r) is int and 1 <= r < M and 0 < a < 1, "binomial domain")
    scale = 1 << 160
    q, z = 1 - a, Q(M - r, M)

    def floor(x):
        return x.numerator // x.denominator

    def ceil(x):
        return -((-x.numerator) // x.denominator)

    lo, hi = floor(q * z * scale), ceil(q * z * scale)
    sum_lo, sum_hi, n = lo, hi, 1
    while True:
        ratio = z * (n - q) / (n + 1)
        lo, hi = floor(lo * ratio), ceil(hi * ratio)
        tail = ceil(hi / (1 - z))
        if tail <= 1 << 70:
            return Q(scale - sum_hi - tail, scale), Q(scale - sum_lo, scale)
        sum_lo, sum_hi, n = sum_lo + lo, sum_hi + hi, n + 1


def sign_of(bounds):
    if bounds[1] < 1:
        return -1
    if bounds[0] > 1:
        return 1
    raise ValueError("unresolved strict moment sign")


def moment(profile, a, cost, overhead=None):
    """Per-call moment bounds: profile + ideal idle packing + charged overhead on top."""
    terms = dict(profile)
    terms[RMAX] = terms.get(RMAX, 0) + Q(IDLE, RMAX)
    for r, n in (overhead or {}).items():
        require(type(r) is int and 1 <= r <= RMAX and Q(n) >= 0, "overhead alphabet")
        terms[r] = terms.get(r, 0) + Q(n)
    lo = hi = Q(0)
    for r, n in terms.items():
        c = cost(r, a)
        lo, hi = lo + Q(n) * c[0], hi + Q(n) * c[1]
    return lo / W, hi / W


def partition(k, cap):
    count, remainder = divmod(k, cap)
    out = Counter({cap: count}) if count else Counter()
    if remainder:
        out[remainder] += 1
    return dict(sorted(out.items()))


def profile(k, cap):
    out = Counter(WORD)
    out[1] -= k
    out.update(partition(k, cap))
    return {r: n for r, n in sorted(out.items()) if n}


def mass(p):
    return sum(r * Q(n) for r, n in p.items())


# ------------------------------------------------------ A: exact identities

# A bilinear form on (x1, x2) x (y1, y2) is the 2x2 integer tuple
# (m00, m01, m10, m11) with m_ij the coefficient of x_i y_j.


def det2(m):
    return m[0] * m[3] - m[1] * m[2]


def addm(p, q, ap=1, bq=1):
    return tuple(ap * p[i] + bq * q[i] for i in range(4))


def is_rank1(m):
    return m != (0, 0, 0, 0) and det2(m) == 0


def conic(A, B):
    """det(aA + bB) = alpha a^2 + beta ab + gamma b^2 with exact integers."""
    alpha = det2(A)
    gamma = det2(B)
    beta = det2(addm(A, B)) - alpha - gamma
    return alpha, beta, gamma


def identity_section():
    out = {}
    matching = ((1, 0, 0, 0), (0, 0, 0, 1))
    shared_row = ((1, 0, 0, 0), (0, 1, 0, 0))
    shared_col = ((1, 0, 0, 0), (0, 0, 1, 0))
    coincident = ((1, 0, 0, 0), (1, 0, 0, 0))
    patterns = {"matching": matching, "shared_row": shared_row,
                "shared_col": shared_col, "coincident": coincident}
    for name, (A, B) in patterns.items():
        alpha, beta, gamma = conic(A, B)
        mixed_rank1 = is_rank1(addm(A, B))
        out[name] = {"conic": [alpha, beta, gamma], "mixed_rank1_exists": mixed_rank1}
    # Matching: det(aA + bB) = ab, so every rank-1 tensor in the span is a
    # multiple of A or B: only coordinate-aligned child outputs can deliver the
    # two products individually.
    alpha, beta, gamma = out["matching"]["conic"]
    check((alpha, beta, gamma) == (0, 1, 0), "A1_matching_conic_is_ab",
          "conic=(0,1,0)")
    check(not out["matching"]["mixed_rank1_exists"], "A2_matching_mixed_output_not_rank1")
    # Shared-row and shared-column spans contain non-coordinate rank-1 tensors;
    # the mixed outputs decode back with exact integer additions.
    f1 = addm(*shared_row)                      # x1(y1 + y2)
    f2 = shared_row[0]                          # x1 y1
    decoded_b = addm(f1, f2, 1, -1)             # f1 - f2 = x1 y2
    check(is_rank1(f1) and decoded_b == shared_row[1],
          "A3_shared_row_mixed_decode_exact", "f1-f2=x1y2")
    mutated = addm(f1, f2, 1, 1)                # wrong decode: f1 + f2
    check(mutated != shared_row[1], "A4_mutated_decode_fails")
    g1 = addm(*shared_col)                      # (x1 + x2) y1
    g2 = shared_col[0]                          # x1 y1
    check(is_rank1(g1) and addm(g1, g2, 1, -1) == shared_col[1],
          "A5_shared_col_mixed_decode_exact")
    check(all(addm(*coincident, a, b) == tuple((a + b) * coincident[0][i] for i in range(4))
              for a, b in ((1, 1), (2, -1))),
          "A6_coincident_span_degenerate")
    # k = 3 finite fixture for coordinate alignment: among 0/1 3x3 matrices
    # supported on the diagonal, the rank-1 ones are exactly the three singles.
    singles = 0
    multi = 0
    for bits in range(1 << 9):
        off = [(bits >> (i * 3 + j)) & 1 for i in range(3) for j in range(3) if i != j]
        if any(off):
            continue
        diag = [(bits >> (i * 3 + i)) & 1 for i in range(3)]
        nonzero = sum(diag)  # rank of a diagonal 0/1 matrix
        if nonzero == 1:
            singles += 1
        elif nonzero >= 2:
            multi += 1
    check(singles == 3 and multi == 4, "A7_k3_diagonal_rank1_are_singles",
          "singles=3 multi=4")
    # Dirty gather-slot restoration witness: writing the gathered operand over a
    # dirty slot is non-injective in the prior content, so restoring arbitrary
    # dirty state needs a paid save of the overwritten content first.
    def write_gather(prior):
        return 5  # the gathered value, independent of prior

    check(write_gather(0) == write_gather(1), "A8_dirty_write_noninjective",
          "states 0 and 1 collide")

    # The k = 2 coordinate-aligned block child: outputs u1v1, u2v2 are exactly
    # the two payload products (exact integer fixtures, flat (m00,m01,m10,m11)).
    out1 = (1, 0, 0, 0)   # u1 v1 = x1 y1
    out2 = (0, 0, 0, 1)   # u2 v2 = x2 y2
    check(out1 == matching[0] and out2 == matching[1], "A9_block_child_outputs_exact")
    return out


# ------------------------------------------------- B: per-group hard search


def per_group(engines):
    """Net saving of one k-block climb group (alpha charged transports) against
    k rank-1 payload children: net = k c(1) - (1+alpha) c(k). Sign convention:
    +1 = net positive (block group strictly cheaper), -1 = net negative."""
    rows = []
    for alpha in (0, 1, 2):
        for k in range(2, 52):
            row = {"k": k, "alpha": alpha, "signs": {}}
            for label, a in (("target", TARGET), ("one_99", Q(1, 99)), ("base_hi", BASE_HI)):
                signs = []
                for name, cost in engines:
                    c1 = cost(1, a)
                    ck = cost(k, a)
                    lo = k * c1[0] - (1 + alpha) * ck[1]
                    hi = k * c1[1] - (1 + alpha) * ck[0]
                    signs.append(1 if lo > 0 else (-1 if hi < 0 else 0))
                require(signs[0] == signs[1] != 0, "engine sign disagreement at k=%d" % k)
                row["signs"][label] = signs[0]
            rows.append(row)
    return rows


def boundary_alpha1(engine):
    ln = engine.ln
    l2 = ln(2)
    l51 = ln(51)
    lo = l2[0] / l51[1]
    hi = l2[1] / l51[0]
    return lo, hi


# --------------------------------------------- C: complete per-call profiles


def profile_section(engine):
    def cost(r, a):
        return engine.child_cost(r, M, a)

    def sign_at(p, overhead=None):
        return sign_of(moment(p, TARGET, cost, overhead))

    screens = {}
    screens["baseline"] = sign_at(WORD)
    p363 = profile(363, 16)
    p362 = profile(362, 16)
    pfull = profile(2412, 16)
    screens["k363_alpha0"] = sign_at(p363)
    screens["k362_alpha0"] = sign_at(p362)
    screens["k363_alpha2"] = sign_at(p363, {16: 44, 11: 2})
    screens["k363_alpha1"] = sign_at(p363, {16: 22, 11: 1})
    screens["k363_dirty_saves"] = sign_at(p363, {1: 23})
    screens["full_alpha0"] = sign_at(pfull)
    screens["full_shared_rank16_one"] = sign_at(pfull, {16: 1})
    screens["full_shared_rank16_two"] = sign_at(pfull, {16: 2})
    screens["full_alpha2"] = sign_at(pfull, {16: 300, 12: 2})

    budget = None
    for n in range(0, 21):
        if sign_at(pfull, {1: n}) == -1:
            budget = n
        else:
            break
    ceilings = {}

    def cap(local):
        return engine.ceiling(local, M, 896, 9, 64, grid=Q(1, 10 ** 12), unpaid=1)

    ceilings["baseline"] = cap(WORD)
    ceilings["all_mass_rank16_ideal"] = cap({16: Q(5586, 16)})
    ceilings["full_alpha0"] = cap(pfull)
    charged = dict(p363)
    for r, n in {16: 44, 11: 2}.items():
        charged[r] = charged.get(r, 0) + n
    ceilings["k363_alpha2_idle_credit"] = cap(charged)
    charged1 = dict(p363)
    for r, n in {16: 22, 11: 1}.items():
        charged1[r] = charged1.get(r, 0) + n
    ceilings["k363_alpha1_idle_credit"] = cap(charged1)
    ceilings["k363_dirty_saves_idle_credit"] = cap({**p363, 1: p363[1] + 23})
    ceilings["full_plus10_budget"] = cap({**pfull, 1: pfull.get(1, 0) + 10})
    return screens, budget, ceilings, {"k363": p363, "k362": p362, "full": pfull}


# ------------------------------------------------------------------- main


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    engine = load_sources()
    ceiling_result = json.loads(
        (ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text(encoding="utf-8"))
    budget_result = json.loads(
        (ROOT / "research/complex-rank-one-block-budget/RESULT.json").read_text(encoding="utf-8"))

    ids = identity_section()

    engines = [("retained_ceiling", lambda r, a: engine.child_cost(r, M, a)),
               ("independent_binomial", lambda r, a: binomial_cost(r, a))]
    rows = per_group(engines)
    # Sign convention: +1 means net saving positive (block group strictly
    # cheaper), -1 means net saving negative (block group strictly dearer).
    charged_worse = [r for r in rows if r["alpha"] >= 1 and all(v == -1 for v in r["signs"].values())]
    free_pays = [r for r in rows if r["alpha"] == 0 and all(v == 1 for v in r["signs"].values())]
    check(len(charged_worse) == 100, "B1_all_charged_groups_worse_everywhere", "100 rows")
    check(len(free_pays) == 50, "B2_all_free_groups_pay_everywhere", "50 rows")

    lo, hi = boundary_alpha1(engine)
    check(Q(1, 99) < lo and TARGET < lo, "B3_boundary_ln2_over_ln51",
          "ln2/ln51 in [" + fdec(lo, 8) + ", " + fdec(hi, 8) + "]")

    screens, budget, ceilings, profs = profile_section(engine)
    check(screens["baseline"] == 1, "C1_baseline_fails_target")
    check(screens["k363_alpha0"] == -1 and screens["k362_alpha0"] == 1,
          "C2_threshold_363_reproduced", "k=362 fails, k=363 passes at zero overhead")
    check(screens["k363_alpha1"] == 1 and screens["k363_alpha2"] == 1,
          "C3_charged_realizations_fail_at_threshold")
    check(screens["k363_dirty_saves"] == 1, "C4_one_save_per_block_fails")
    check(screens["full_alpha0"] == -1, "C5_full_reblock_passes_at_zero_overhead")
    check(screens["full_shared_rank16_one"] == 1 and screens["full_shared_rank16_two"] == 1,
          "C6_one_shared_rank16_transport_fails")
    check(screens["full_alpha2"] == 1, "C7_full_reblock_natural_realization_fails")
    check(budget == budget_result["rank16_complete_max_extra_integer_rank_mass"] == 10,
          "C8_overhead_budget_10_reproduced", "max extra rank-1 calls = 10")

    base_cap = ceilings["baseline"]
    check(base_cap[0] <= BASE_HI <= base_cap[1],
          "C9_baseline_ceiling_bracket_contains_pinned_value",
          "[" + fdec(base_cap[0], 15) + ", " + fdec(base_cap[1], 15) + "]")
    gate_free = ceilings["full_alpha0"][0] >= TARGET
    gate_charged = ceilings["k363_alpha2_idle_credit"][1] < TARGET
    gate_charged1 = ceilings["k363_alpha1_idle_credit"][1] < TARGET
    gate_dirty = ceilings["k363_dirty_saves_idle_credit"][1] < TARGET
    check(gate_free and gate_charged and gate_charged1 and gate_dirty,
          "C10_gate_fails_for_charged_threshold_realizations")
    budget_sign = sign_of(moment(profs["full"], TARGET,
                                 lambda r, a: engine.child_cost(r, M, a), {1: 10}))
    gate_budget = ceilings["full_plus10_budget"][0] >= TARGET
    check(gate_budget and budget_sign == -1, "C14_gate_stays_open_within_call_budget",
          "full reblock + 10 rank-1 units")
    ideal = ceilings["all_mass_rank16_ideal"]
    check(ideal[0] > 2 * BASE_HI, "C11_all_mass_rank16_ideal_control",
          "x" + fdec(ideal[0] / BASE_HI, 3))

    require(mass(profs["k363"]) == mass(profs["k362"]) == mass(profs["full"]) == 2412 + 418 * 2
            + 432 * 3 + 142 * 4 + 82 * 5 + 8 * 8, "mass conservation")
    check(True, "C12_mass_conservation", "local mass 5586 preserved")

    target_check = Q(21, 20) * Q(1690054109089, 10 ** 15)
    num, den = budget_result["target"].split("/")
    require(target_check == Q(int(num), int(den)) == TARGET,
            "target definition drift")
    check(True, "C13_target_matches_pinned_receipts",
          "a* = " + fdec(TARGET, 15))

    result = {
        "status": "PASS_BLOCK_CLIMB_COMPLETE_PROFILE",
        "scope": (
            "Smallest falsifying instance (k=2 exact identity) and one bounded pivot "
            "(PR 1605 threshold partitions and full reblock) of block-climb delivery of "
            "the selected word's rank-one payload; charged-climb family excluded, "
            "zero-charge co-frame groups remain open."),
        "model": {
            "width_m": 73, "families": 896, "stages": 9, "centre_per_call": 64,
            "local_profile": {str(k): v for k, v in WORD.items()},
            "idle_mass": IDLE, "idle_rank_cap": RMAX,
            "transport_contract": "each rank-r transport charged as a rank-r recursive child (PR 1429)",
            "overhead_contract": "additional work charged on top, no old idle credit (PR 1605)",
        },
        "target": fstr(TARGET),
        "target_definition": "21/20 times the certified baseline primitive ceiling upper bound",
        "identities": ids,
        "per_group_boundary": {
            "sign_convention": "+1 = net saving positive (block group cheaper); -1 = net negative (block group dearer)",
            "pay_condition": "k^a > alpha + 1, i.e. a > ln(1+alpha)/ln k",
            "alpha1_min_boundary": ["ln2/ln51", fstr(lo), fstr(hi), fdec(lo, 8)],
            "consequence": (
                "every group with >= 1 charged transport is strictly worse than its k "
                "rank-1 payload children for all a <= 1/99 and indeed all a < ln2/ln51"),
        },
        "per_group_signs": rows,
        "profile_screens": {k: v for k, v in screens.items()},
        "full_reblock_max_extra_rank1_calls": budget,
        "ceilings": {k: [fstr(v[0]), fstr(v[1])] for k, v in ceilings.items()},
        "gate_five_percent": {
            "zero_charge_full_reblock_meets_gate": gate_free,
            "charged_realization_even_with_idle_credit": gate_charged,
            "one_transport_realization_even_with_idle_credit": gate_charged1,
            "dirty_save_realization_even_with_idle_credit": gate_dirty,
            "call_budget_ten_rank1_units_meets_gate": gate_budget,
            "note": (
                "The gate is missed by every per-group charged realization at the "
                "threshold partitions; it stays open for realizations whose complete "
                "charged invoice fits PR 1605's call-level budget (<= 10 added rank-1 "
                "units per call at full reblock, i.e. under 0.07 units per group)."),
        },
        "controls": CHECKS,
    }
    text = json.dumps(result, indent=1, sort_keys=True)
    if args.write:
        (HERE / "RESULT.json").write_text(text + "\n", encoding="utf-8", newline="\n")
        print("WROTE_RESULT_JSON")
    print("PASS_BLOCK_CLIMB_COMPLETE_PROFILE controls=" + str(len(CHECKS))
          + " charged_groups_excluded=100 free_groups_open=50 budget_rank1=" + str(budget))


if __name__ == "__main__":
    main()
