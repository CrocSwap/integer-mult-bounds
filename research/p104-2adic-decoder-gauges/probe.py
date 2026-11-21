#!/usr/bin/env python3
"""Exact finite checks for the 2-adic gaugeable-subset decoder bound.

P104 labels and the non-vacuity decoder are read from the pinned #7852 Lean
sources alongside this script.  No solver result or exhaustive statement about
all decoders is inferred from the example checks.
"""
import ast
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
BASE = HERE / "LinP104Base.lean"
INST = HERE / "LinP104FreeInstBase.lean"
assert sha256(BASE.read_bytes()).hexdigest() == "20a8474716ae87b22a325b524b826ba7b354239e36a36c78c1b76e8106d3952d"
assert sha256(INST.read_bytes()).hexdigest() == "161d8c08505f6e09d275555027f14fdad6aec04f7a855a637a178352e35c9b8e"


def table(src, name):
    match = re.search(r"^def " + re.escape(name) + r"\s*:[^\n]*?:=\s*(\[.*\])$", src, re.M)
    assert match, name
    return ast.literal_eval(match.group(1))


base = BASE.read_text()
inst = INST.read_text()
labels = table(base, "labMasks")
xlabels = table(base, "xMasks")
bm = table(base, "bmMasks")
ct = table(inst, "ctL")
G = table(inst, "GbL")
N = 104
assert len(labels) == len(xlabels) == len(ct) == N
assert all(x.bit_count() % 2 == 1 for x in labels)
Q = [[(a & b).bit_count() % 2 for b in labels] for a in labels]
assert all(Q[t][s] == 1 ^ (sum(((bm[j] & xlabels[t]).bit_count() & 1) * ((xlabels[s] >> j) & 1) for j in range(8)) & 1) for t in range(N) for s in range(N))
assert Q[0][6] == 1


def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def rank2_reference(rows):
    """Separate dense Gaussian elimination checks the packed-rank routine."""
    rows = [list(r) for r in rows]
    if not rows:
        return 0
    rank = 0
    for j in range(len(rows[0])):
        p = next((i for i in range(rank, len(rows)) if rows[i][j]), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i][j]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def valuation(a):
    assert a != 0
    a = F(a)
    n, d = abs(a.numerator), a.denominator
    return ((n & -n).bit_length() - 1) - ((d & -d).bit_length() - 1)


def pow2(a):
    return F(2 ** a, 1) if a >= 0 else F(1, 2 ** (-a))


def check(w, u, expect=True):
    """All 10816 rational live-pattern cells, price and raw good ports."""
    total = [[F(0) for _ in range(N)] for _ in range(N)]
    prices = []
    for wi, ui in zip(w, u):
        assert all(c != 0 for c in wi.values())
        assert all(c != 0 for c in ui.values())
        for t, a in wi.items():
            for s, b in ui.items():
                total[t][s] += a * b
        smask = list(ui)
        row_price = rank2([sum(Q[t][s] << j for j, s in enumerate(smask)) for t in wi])
        assert row_price == rank2_reference([[Q[t][s] for s in smask] for t in wi])
        prices.append(row_price)
    errors = [(t, s, str(total[t][s]), str(int(t == s)))
              for t in range(N) for s in range(N)
              if Q[t][s] and total[t][s] != int(t == s)]
    assert bool(not errors) == expect, errors[:4]
    amin, bmin = {}, {}
    for t in range(N):
        aa = [valuation(x[t]) for x in w if t in x]
        bb = [valuation(x[t]) for x in u if t in x]
        assert aa and bb
        amin[t], bmin[t] = min(aa), min(bb)
    good = [t for t in range(N) if amin[t] + bmin[t] >= 0]
    poisoned = [t for t in range(N)
                if any(t in wi and t in ui and valuation(wi[t]) + valuation(ui[t]) < 0
                       for wi, ui in zip(w, u))]
    return {"errors": errors, "price": sum(prices), "price_counts": dict(Counter(prices)),
            "good": good, "poisoned": poisoned}


def constraints(w, u, selected):
    """Edges a->b mean lambda_b <= lambda_a + v2(w_a(t) u_b(t))."""
    edges = []
    for t in selected:
        left = [(k, valuation(v[t])) for k, v in enumerate(w) if t in v]
        right = [(k, valuation(v[t])) for k, v in enumerate(u) if t in v]
        edges.extend((a, b, av + bv, t) for a, av in left for b, bv in right)
    return edges


def gauge(w, u, selected):
    """Bellman-Ford feasibility; not a maximum subset or mass solver."""
    edges = constraints(w, u, selected)
    d = [0] * len(w)
    for _ in range(len(d)):
        changed = False
        for a, b, c, _t in edges:
            if d[b] > d[a] + c:
                d[b] = d[a] + c
                changed = True
        if not changed:
            return d
    return None


def apply_gauge(w, u, d):
    return ([{t: c * pow2(d[k]) for t, c in wi.items()} for k, wi in enumerate(w)],
            [{t: c / pow2(d[k]) for t, c in ui.items()} for k, ui in enumerate(u)])


def restricted_certificate(w, u, selected, d):
    """Check the conjugated/reduced identity and both rank inequalities."""
    w, u = apply_gauge(w, u, d)
    alpha = {t: min(valuation(wi[t]) for wi in w if t in wi) for t in selected}
    rho = [{t: v / pow2(alpha[t]) for t, v in wi.items() if t in alpha} for wi in w]
    ups = [{t: v * pow2(alpha[t]) for t, v in ui.items() if t in alpha} for ui in u]
    assert all(valuation(v) >= 0 for z in rho + ups for v in z.values())

    def mod2(v):
        assert v.denominator % 2 == 1
        return v.numerator % 2

    for t in selected:
        for s in selected:
            sm = sum(mod2(a.get(t, F(0))) * mod2(b.get(s, F(0)))
                     for a, b in zip(rho, ups)) % 2
            assert Q[t][s] * sm == int(t == s)
    restricted_rank = reduced_rank = 0
    for wi, ui in zip(rho, ups):
        left, right = list(wi), list(ui)
        restricted_rank += rank2([sum(Q[t][s] << j for j, s in enumerate(right)) for t in left])
        reduced_rank += rank2([sum((mod2(wi[t]) * Q[t][s] * mod2(ui[s])) << j
                                   for j, s in enumerate(right)) for t in left])
    full_price = check(w, u)["price"]
    assert len(selected) <= reduced_rank <= restricted_rank <= full_price
    return {"ports": len(selected), "sum_reduced_ranks": reduced_rank,
            "sum_restricted_pairing_ranks": restricted_rank, "full_price": full_price}


def matching(size):
    remaining = set(range(N)) - {0, 6}
    result = [(0, 6)]
    while len(result) < size:
        a = min(remaining)
        candidates = [b for b in sorted(remaining) if b != a and Q[a][b]]
        assert candidates
        b = candidates[0]
        result.append((a, b))
        remaining -= {a, b}
    return result


def block_example(kind, n_pairs, extra_bad=False):
    pairs = matching(n_pairs)
    occupied = set(sum(([a, b] for a, b in pairs), []))
    w, u = [], []
    for a, b in pairs:
        if kind == "defect":
            # A = [[1,1],[1,5]], A^-T = [[5/4,-1/4],[-1/4,1/4]].
            w.extend([{a: F(1), b: F(1)}, {a: F(1), b: F(5)}])
            u.extend([{a: F(5, 4), b: F(-1, 4)}, {a: F(-1, 4), b: F(1, 4)}])
        elif kind == "recoverable":
            # Integral identity factorization, followed by one 1/4 row gauge.
            w.extend([{a: F(1)}, {a: F(1, 4), b: F(1, 4)}])
            u.extend([{a: F(1), b: F(-1)}, {b: F(4)}])
        else:
            raise ValueError(kind)
    for t in sorted(set(range(N)) - occupied):
        w.append({t: F(1)})
        u.append({t: F(1)})
    if extra_bad:
        t = min(set(range(N)) - occupied)
        w.extend([{t: F(1, 4)}, {t: F(-1, 4)}])
        u.extend([{t: F(1)}, {t: F(1)}])
    return w, u, pairs


def e8_example():
    w = [{t: F(ct[t][k], 2) for t in range(N) if ct[t][k]} for k in range(8)]
    vs = [[sum(G[k][i] * ct[t][i] for i in range(8)) for t in range(N)] for k in range(8)]
    u = [{t: F(vs[k][t]) for t in range(N) if vs[k][t]} for k in range(8)]
    return w, u


out = {}
w, u, pairs = block_example("defect", 24)
r = check(w, u)
assert r["price"] == 104 and len(r["good"]) == 56
assert len(r["poisoned"]) == 48 and set(r["poisoned"]) == set(range(N)) - set(r["good"])
assert gauge(w, u, r["good"]) is not None and gauge(w, u, range(N)) is None
assert w[0][0] * u[0][6] == F(-1, 4) and w[1][0] * u[1][6] == F(1, 4)
assert all(any(((x & xlabels[t]).bit_count() & 1) != (int(t in w[0]) & 1)
               for t in range(N)) for x in range(256))
out["48_intrinsic_defects"] = {"rows": len(w), "pairs": pairs, "good_ports": len(r["good"]),
                               "gauge_invariant_poisoned_ports": len(r["poisoned"]),
                               "price": r["price"], "live_quarter_cancellation": ["-1/4", "1/4"],
                               "first_w_row_non_linear_mod2": True}
out["48_intrinsic_defects"]["rank_certificate"] = restricted_certificate(w, u, r["good"], gauge(w, u, r["good"]))
wp = [dict(x) for x in w]
wp[0][0] += 1
bad = check(wp, u, expect=False)
assert any(t == 0 and s == 6 for t, s, _, _ in bad["errors"])
out["48_defects_perturbation"] = {"detected": True, "first_errors": bad["errors"][:3]}

w, u, _ = block_example("defect", 24, extra_bad=True)
r = check(w, u)
assert r["price"] == 106 and len(r["good"]) == 55 and len(r["poisoned"]) == 49
assert gauge(w, u, r["good"]) is not None and gauge(w, u, range(N)) is None
out["49_intrinsic_defects"] = {"rows": len(w), "good_ports": len(r["good"]),
                               "gauge_invariant_poisoned_ports": len(r["poisoned"]),
                               "price": r["price"], "method_floor": len(r["good"])}
out["49_intrinsic_defects"]["rank_certificate"] = restricted_certificate(w, u, r["good"], gauge(w, u, r["good"]))

w, u, _ = block_example("recoverable", 25)
r = check(w, u)
assert r["price"] == 104 and len(r["good"]) == 54
d = gauge(w, u, range(N))
assert d is not None
wn, un = apply_gauge(w, u, d)
rn = check(wn, un)
assert len(rn["good"]) == N and rn["price"] == r["price"]
out["row_gauge_recovers_all_ports"] = {"raw_good_ports": len(r["good"]),
                                      "good_ports_after_gauge": len(rn["good"]),
                                      "gauge_min": min(d), "gauge_max": max(d), "price": r["price"]}
out["row_gauge_recovers_all_ports"]["rank_certificate"] = restricted_certificate(w, u, list(range(N)), d)

w, u = e8_example()
r = check(w, u)
assert r["price"] == 69
out["honest_e8_control"] = {"rows": len(w), "price": r["price"], "raw_good_ports": len(r["good"]),
                             "gauge_invariant_poisoned_ports": len(r["poisoned"]),
                             "at_most_gaugeable_ports": N - len(r["poisoned"])}

print(json.dumps(out, indent=2, sort_keys=True))
