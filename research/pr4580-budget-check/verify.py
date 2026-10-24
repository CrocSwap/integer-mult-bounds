#!/usr/bin/env python3
"""Independent arithmetic check of PR #4580 (Matarener): the p3 H-branch boundary budget at kappa = 0.00302015.

The signed complex and BIT rank profiles are taken from the same main sources #4580 uses (controller_tariff.geometry(3,
43) with kernel H; the BIT probe with the three-row minimum completion). Everything else is recomputed here with this
file's own exact arithmetic, never the sources' h_interval:
  * certified powers r^(1-s) from atanh logarithms and range-reduced exp series, rounded outward on a 2^-256 grid;
  * raw surpluses 616 / 645; budgets 322 / 397 at s = 0.00302015 (largest k with certified moment - k > 0), and
    budget + 1 certified negative;
  * own certified saving-root brackets (width <= 1e-12) for bills 0, 224/222, 448/444: every reported positive_at is
    certified positive and every reported negative_at lies within #4580's bisection width (0.02/2^26, about 3e-10) of the root, but two printed negative_at
    strings (complex bill 0, BIT bill 222) are 10-decimal roundings that fall just below the root, where the moment is
    still positive; the direct bills 672 / 666 fail at s = 0;
  * the native H112 from main's rebuild_native: own exact rank(H - I) = 8, all 112 rows and columns of H - I nonzero,
    H^2 = I;
  * 112 distinct complex query lines and 111 distinct BIT lines up to sign.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KR = ROOT / "research/kappa-rebuild"
DEP = ROOT / "research/kappa-0023-productive-jobs/dependencies/kappa-next-regime"
sys.path[:0] = [str(KR / "architecture"), str(KR / "bit"), str(DEP / "bit-compression/carrier-reuse/reference")]
RECORD = Q("0.00302015")
GRID = Q(1, 2 ** 256)
REPORTED = {  # #4580 RESULT.json brackets (head 62545a03)
    "complex": {0: ("0.0063799042", "0.0063799044"), 224: ("0.0040422291", "0.0040422294"),
                448: ("0.0017248833", "0.0017248836")},
    "bit": {0: ("0.0079333532", "0.0079333535"), 222: ("0.0051761594", "0.0051761597"),
            444: ("0.0024471104", "0.0024471107")},
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def down(x):
    return Q((x / GRID).__floor__()) * GRID


def up(x):
    return Q((x / GRID).__ceil__()) * GRID


def ln_bounds(n, terms=90):
    n = Q(n)
    k = 0
    while n >= 2:
        n /= 2
        k += 1

    def series(y):
        z = (y - 1) / (y + 1)
        s, p = Q(0), z
        for j in range(terms):
            s += 2 * p / (2 * j + 1)
            p *= z * z
        return down(s), up(s + 2 * p / ((2 * terms + 1) * (1 - z * z)))

    a, b = series(n)
    c, d = series(Q(2))
    return a + k * c, b + k * d


def exp_bounds(x):
    """Outward bounds for exp(x), x >= 0 rational."""
    k = 0
    while x > Q(1, 2):
        x /= 2
        k += 1
    t, s = Q(1), Q(1)
    for n in range(1, 40):
        t = t * x / n
        s += t
    lo, hi = down(s), up(s + 2 * t * x / 40)
    for _ in range(k):
        lo, hi = down(lo * lo), up(hi * hi)
    return lo, hi


_CACHE = {}


def power(r, s):
    """Certified [lo, hi] for r^(1-s), r >= 1."""
    key = (r, s)
    if key not in _CACHE:
        if r == 1:
            _CACHE[key] = (Q(1), Q(1))
        else:
            a, b = ln_bounds(r)
            _CACHE[key] = (exp_bounds((1 - s) * a)[0], exp_bounds((1 - s) * b)[1])
    return _CACHE[key]


def moment(signed, s):
    lo = hi = Q(0)
    for r, n in signed.items():
        a, b = power(r, s)
        lo += n * (a if n >= 0 else b)
        hi += n * (b if n >= 0 else a)
    return lo, hi


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def profiles():
    import controller_tariff as T
    import mixed_forest_search as F
    windows, targets, _ = T.geometry(3, 43)
    case = F.verify(3, 6, T.simple_p3(), "H", custom_windows=windows, custom_targets=targets)
    cx = Counter(case["signed"])
    probe = json.loads((KR / "bit/PR589-H-GLOBAL-PROBE.json").read_text())
    audit = json.loads((KR / "transfer-audit/h-branch/BIT-MINIMUM-COMPLETION-AUDIT.json").read_text())
    bt = Counter({int(r): n for r, n in probe["targets"].items()})
    bt.subtract(Counter({int(r): n for r, n in audit["p3"]["raw_paid"].items()}))
    return {"complex": cx, "bit": bt}


def side(name, signed):
    margin = sum(r * n for r, n in signed.items())
    need(margin == {"complex": 616, "bit": 645}[name], f"{name} raw surplus")
    lo, hi = moment(signed, RECORD)
    budget = lo.numerator // lo.denominator
    if Q(budget) == lo:
        budget -= 1
    need(budget == {"complex": 322, "bit": 397}[name], f"{name} budget")
    need(hi - (budget + 1) < 0, f"{name}: budget + 1 certified negative")
    roots, mislabelled = {}, []
    for bill, (pos, neg) in REPORTED[name].items():
        prof = Counter(signed)
        prof[1] -= bill
        lo_s, hi_s = Q(0), Q("0.02")
        need(moment(prof, lo_s)[0] > 0 and moment(prof, hi_s)[1] < 0, "outer bracket")
        while hi_s - lo_s > Q(1, 10 ** 12):
            mid = (lo_s + hi_s) / 2
            a, b = moment(prof, mid)
            if a > 0:
                lo_s = mid
            elif b < 0:
                hi_s = mid
            else:
                break
        need(hi_s - lo_s <= Q(1, 10 ** 12), "own certified bracket width <= 1e-12")
        need(moment(prof, Q(pos))[0] > 0, f"{name} reported positive_at certified positive (bill {bill})")
        need(abs(Q(neg) - hi_s) < Q(4, 10 ** 10), f"{name} reported negative_at within #4580's bisection width of the root (bill {bill})")
        if not moment(prof, Q(neg))[1] < 0:
            mislabelled.append(bill)  # the printed 10-decimal endpoint lies just below the root
        roots[str(bill)] = [f"{float(lo_s):.13f}", f"{float(hi_s):.13f}"]
    need(mislabelled == {"complex": [0], "bit": [222]}[name], f"{name}: rounded negative_at endpoints identified")
    direct = {"complex": 672, "bit": 666}[name]
    prof = Counter(signed)
    prof[1] -= direct
    need(moment(prof, Q(0))[1] < 0, f"{name}: direct bill fails at s = 0")
    return {"raw_surplus": int(margin), "budget": int(budget), "moment_at_record": [float(lo), float(hi)],
            "certified_root_brackets": roots, "reported_negative_at_not_negative_for_bills": mislabelled}


def rank(rows):
    rows = [list(r) for r in rows]
    rk, cols = 0, len(rows[0])
    for c in range(cols):
        piv = None
        for i in range(rk, len(rows)):
            if rows[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        pv = rows[rk][c]
        for i in range(len(rows)):
            if i != rk and rows[i][c] != 0:
                f = rows[i][c] / pv
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[rk])]
        rk += 1
    return rk


def native():
    n = load(DEP / "direct-decoder/native_common.py", "chk_native_common")
    reb = load(KR / "complex/rebuild_native.py", "chk_rebuild_native")
    packet, _ = n.load_sources()
    H = reb.geometry(packet)["H"]
    size = len(H)
    h = [[Q(row.get(j, 0)) for j in range(size)] for row in H]
    m = [[h[i][j] - (1 if i == j else 0) for j in range(size)] for i in range(size)]
    need(size == 112 and rank(m) == 8, "rank(H - I) = 8")
    need(all(any(r) for r in m) and all(any(m[i][j] for i in range(size)) for j in range(size)), "full support")
    for i in range(size):
        for j in range(size):
            need(sum(h[i][k] * h[k][j] for k in range(size)) == (1 if i == j else 0), "H^2 = I")
    return {"ports": size, "rank_H_minus_I": 8}


def lines():
    phases = json.loads((DEP / "direct-decoder/sources/DATA-PHASES.json").read_text())
    qs = [r["q"] for r in phases["recipes"]]
    need(len(qs) == 112 and len(set(qs)) == 112, "112 distinct complex query lines")
    word = json.loads(gzip.decompress((KR / "bit/sources/pr589-regenerated/WORD.json.gz").read_bytes()))
    ls = [tuple(Q(x) for x in q) for q in word["lines"]]
    need(len(ls) == 111 and len({max(q, tuple(-x for x in q)) for q in ls}) == 111, "111 distinct BIT lines")
    return {"complex": 112, "bit": 111}


def main():
    for r in range(2, 200):
        a, b = power(r, Q(0))
        need(a <= r <= b and b - a < Q(1, 10 ** 50), "power control at s = 0")
    p = profiles()
    report = {"status": "PASS_PR4580_BUDGET_CHECK", "complex": side("complex", p["complex"]), "bit": side("bit", p["bit"]),
              "native_H112": native(), "distinct_lines": lines(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
