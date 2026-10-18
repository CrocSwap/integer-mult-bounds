#!/usr/bin/env python3
"""Exact premises and controls for PROOF.md. Apache-2.0.

Arham Tahir, with substantial OpenAI Codex assistance. The quantified complex
argument is written, not inferred from finite factor-mixing examples.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {"research/p112-single-lift/geometry.py",
          "research/complex-frame-pair-decoders/PROOF.md"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources(sources):
    rows = [r for r in sources["files"] if r["usage"] == "input"]
    need(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
         "complete live source inventory")
    for row in rows:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
             == row["sha256"], "live source digest: " + row["path"])


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def witnesses(rows, indices):
    selected, previous = [], []
    for i in indices:
        if rank2(previous + [rows[i]]) > len(previous):
            previous.append(rows[i])
            selected.append(i)
    return selected


def mask(indices):
    return sum(1 << i for i in indices)


def pairing_rank(pairing, left, right):
    target = mask(right)
    return rank2(pairing[i] & target for i in left)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def model():
    """Doubled Euclidean roots, independently of the predecessor module."""
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            r = [0] * 8
            r[i], r[j] = a, b
            roots.add(max(tuple(r), tuple(-v for v in r)))
    for r in product((-1, 1), repeat=8):
        if r.count(-1) % 2 == 0:
            roots.add(max(r, tuple(-v for v in r)))
    frame = []
    for j in range(4):
        for sign in (1, -1):
            r = [0] * 8
            r[2*j], r[2*j+1] = 2, 2*sign
            frame.append(tuple(r))
    need(len(roots) == 120 and set(frame) <= roots, "120 root lines and frame")
    live = sorted(roots - set(frame))
    x = [[dot(r, f) // 4 for f in frame] for r in live]
    b = [mask(j for j, s in enumerate(live) if (dot(r, s)//4 + 1) % 2)
         for r in live]
    need(len(live) == 112 and rank2(b) == 9, "P112 and ambient binary rank nine")
    need(all(b[i] >> i & 1 for i in range(112)), "binary diagonal one")
    need(all(dot(x[i], x[j]) == dot(live[i], live[j])//2
             for i in range(112) for j in range(112)), "XX^transpose = 2G")
    spec = importlib.util.spec_from_file_location("pinned_geometry", ROOT /
                         "research/p112-single-lift/geometry.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    old = source.build()
    source.check_geometry(old)
    lookup = {max(tuple(r), tuple(-v for v in r)): i
              for i, r in enumerate(old["roots"])}
    need(set(lookup) == set(live), "predecessor live-root binding")
    for i, r in enumerate(live):
        oi = lookup[r]
        sign = 1 if tuple(old["roots"][oi]) == r else -1
        need(x[i] == [sign*v for v in old["X"][oi]], "coordinate column binding")
        for j, s in enumerate(live):
            oj = lookup[s]
            value = source.parity(old["duals"][oi] & old["labels"][oj])
            need(value == (b[i] >> j & 1), "all 12544 pairing entries bound")
    return live, x, b


class QI:
    """Exact Q(i) scalars, with ordinary transpose."""
    def __init__(self, r=0, i=0):
        self.r, self.i = Fraction(r), Fraction(i)

    @staticmethod
    def cast(value):
        return value if isinstance(value, QI) else QI(value)

    def __add__(self, other):
        o = self.cast(other)
        return QI(self.r+o.r, self.i+o.i)

    __radd__ = __add__

    def __neg__(self):
        return QI(-self.r, -self.i)

    def __sub__(self, other):
        return self + -self.cast(other)

    def __mul__(self, other):
        o = self.cast(other)
        return QI(self.r*o.r-self.i*o.i, self.r*o.i+self.i*o.r)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = self.cast(other)
        den = o.r*o.r+o.i*o.i
        need(bool(den), "nonzero exact denominator")
        return QI((self.r*o.r+self.i*o.i)/den,
                  (self.i*o.r-self.r*o.i)/den)

    def __bool__(self):
        return bool(self.r or self.i)

    def __eq__(self, other):
        o = self.cast(other)
        return self.r == o.r and self.i == o.i


def support(vector):
    return [i for i, v in enumerate(vector) if v]


def mix(x, u, v, matrix):
    a, b, c, d = (QI.cast(t) for row in matrix for t in row)
    det = a*d-b*c
    need(bool(det), "invertible two-term basis change")
    left = [[a*t+c*s for t, s in zip(x, u)],
            [b*t+d*s for t, s in zip(x, u)]]
    right = [[(d*t-b*s)/det for t, s in zip(x, v)],
             [(-c*t+a*s)/det for t, s in zip(x, v)]]
    return left, right


def check_identity(x, u, v, left, right):
    need(all(left[0][i]*right[0][j] + left[1][i]*right[1][j]
             == x[i]*x[j]+u[i]*v[j]
             for i in range(112) for j in range(112)),
         "two-term ordinary-transpose identity")


def check_free(pairing, u, v):
    need(pairing_rank(pairing, support(u), support(v)) == 0,
         "free correction must have zero pairing rectangle")


def rankq(rows):
    basis = {}
    for original in rows:
        row = list(map(Fraction, original))
        for k, previous in sorted(basis.items()):
            if row[k]:
                c = row[k]
                row = [a-c*b for a, b in zip(row, previous)]
        k = next((k for k, v in enumerate(row) if v), None)
        if k is not None:
            basis[k] = [v/row[k] for v in row]
    return len(basis)


def run():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    check_sources(pins)
    live, x, pairing = model()
    columns = [[row[k] for row in x] for k in range(8)]
    stars = [support(col) for col in columns]
    slices, cross_hist, cross_example = [], Counter(), None
    for k, star in enumerate(stars):
        need(len(star) == 56, "coordinate star size 56")
        need(rank2(pairing[i] for i in star) == 8, "coordinate label span eight")
        need(pairing_rank(pairing, star, star) == 8, "nondegenerate star pairing")
        subsets = []
        for j in range(112):
            subset = [i for i in star if pairing[i] >> j & 1]
            need(rank2(pairing[i] for i in subset) == 7, "affine slice span seven")
            subsets.append(subset)
            slices.append({"coordinate": k, "root": j, "size": len(subset),
                           "mask": hex(mask(subset)),
                           "basis": witnesses(pairing, subset), "rank": 7})
        for j, left in enumerate(subsets):
            for h, right in enumerate(subsets):
                cost = pairing_rank(pairing, left, right)
                need(cost >= 6, "dense survivor pairing floor six")
                cross_hist[str(cost)] += 1
                if cost == 6 and cross_example is None:
                    cross_example = {"coordinate": k, "left_root": j, "right_root": h}
    need(len(slices) == 896 and sum(cross_hist.values()) == 100352,
         "complete slice and cross-pair coverage")
    need(cross_example is not None, "actual rank-six cross slice")
    i, j = next((i, j) for i in range(112) for j in range(112)
                if not (pairing[i] >> j & 1))
    need(i != j and rankq(x) == 8, "coordinate rank eight")
    need(rankq([row + [int(t == i)] for t, row in enumerate(x)]) == 9
         and rankq([row + [int(t == j)] for t, row in enumerate(x)]) == 9,
         "singleton correction has rank-nine factors and product")
    u = [QI(int(t == i)) for t in range(112)]
    v = [QI(int(t == j)) for t in range(112)]
    matrices = [("identity", [[1, 0], [0, 1]]),
                ("lower shear", [[1, 0], [2, 1]]),
                ("upper shear", [[1, 3], [0, 1]]),
                ("antitriangular", [[0, 2], [1, 3]]),
                ("dense real", [[1, 2], [3, 4]]),
                ("dense complex", [[1, QI(0, 1)], [QI(0, 1), 1]])]
    fixtures = []
    for name, m in matrices:
        left, right = mix(columns[0], u, v, m)
        check_free(pairing, u, v)
        check_identity(columns[0], u, v, left, right)
        costs = [pairing_rank(pairing, support(a), support(b))
                 for a, b in zip(left, right)]
        need(sum(costs) >= 8, "fixture COPY lower bound")
        fixtures.append({"name": name, "costs": costs,
                         "whole_decoder_cost": 56+sum(costs), "entries": 12544})
    pivot = stars[0][0]
    u2 = [QI(columns[0][t] if not (pairing[t] >> pivot & 1) else 0)
          for t in range(112)]
    v2 = [QI(columns[0][t] if t == pivot else 0) for t in range(112)]
    left, right = mix(columns[0], u2, v2, [[1, 1], [-1, 1]])
    check_free(pairing, u2, v2)
    check_identity(columns[0], u2, v2, left, right)
    costs = [pairing_rank(pairing, support(a), support(b)) for a, b in zip(left, right)]
    need(sum(costs) >= 12, "nonzero dense-rectangle bound")
    fixtures.append({"name": "odd-star cancellation", "costs": costs,
                     "whole_decoder_cost": 56+sum(costs), "entries": 12544,
                     "free_support_sizes": [len(support(u2)), len(support(v2))]})
    zeros, copy = [QI()]*112, [QI(t) for t in columns[0]]
    left, right = mix(columns[0], zeros, copy, [[1, 1], [2, 1]])
    check_identity(columns[0], zeros, copy, left, right)
    costs = [pairing_rank(pairing, support(a), support(b)) for a, b in zip(left, right)]
    need(sorted(costs) == [0, 8], "degenerate sharp dense control")
    fixtures.append({"name": "zero factor dense boundary", "costs": costs,
                     "whole_decoder_cost": 64, "entries": 12544})
    controls = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("false claim accepted: " + name)

    reject("strengthen affine slice span to eight", lambda:
           need(slices[0]["rank"] == 8, "slice dimension"))
    reject("strengthen every slice cross pairing to seven", lambda:
           need(cross_hist.get("6", 0) == 0, "actual rank-six cross slice"))
    reject("call a diagonal singleton correction free", lambda: check_free(pairing, u, u))
    reject("singular factor change", lambda: mix(columns[0], u, v, [[1, 2], [2, 4]]))
    left, right = mix(columns[0], u, v, [[1, 2], [3, 4]])
    right[0][0] = right[0][0] + 1
    reject("mutate inverse-transpose coefficient", lambda:
           check_identity(columns[0], u, v, left, right))
    bad = json.loads(json.dumps(pins))
    bad["files"] = [r for r in bad["files"]
                    if r["path"] != "research/p112-single-lift/geometry.py"]
    reject("omit a live source", lambda: check_sources(bad))
    bad = json.loads(json.dumps(pins))
    next(r for r in bad["files"] if r["usage"] == "input")["sha256"] = "0"*64
    reject("corrupt a live source digest", lambda: check_sources(bad))
    reject("claim rank-eight masked product", lambda:
           need(rankq([row+[int(t == i)] for t, row in enumerate(x)]) == 8,
                "rank-nine example"))
    reject("apply dense bound to a zero outer product", lambda:
           need(min(costs) >= 6, "degenerate branch is essential"))
    return {"status": "PASS_P112_FREE_RECTANGLE_MIXING", "sources": pins,
            "roots": [list(r) for r in live],
            "coordinate_stars": [{"support": hex(mask(s)), "span": 8, "pairing": 8}
                                 for s in stars], "slices": slices,
            "cross_pair_count": 100352,
            "cross_pair_histogram": dict(sorted(cross_hist.items())),
            "rank_six_example": cross_example,
            "rank_nine_odd_singleton": [i, j], "fixtures": fixtures,
            "negative_controls": controls,
            "theorem": "One arbitrary cost-zero rectangle mixed with one original P112 coordinate term by GL(2,C) has replacement COPY rank sum at least eight and whole-decoder cost at least64. For nonzero u,v and two active coordinate products, each replacement has rank at least six.",
            "scope": "Written PROOF.md plus exact finite premises; separate-term COPY rank and concave power bill only. No physical word, full invoice, native admission, new kappa, all-size or full multiplication theorem."}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    receipt = run()
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    else:
        need(canonical(receipt) == canonical(json.loads(args.check.read_text())),
             "complete mathematical receipt mismatch")
    print("PASS_P112_FREE_RECTANGLE_MIXING slices=896 cross_pairs=100352 "
          "fixtures=8 controls=9 copy_floor=64 no_new_kappa")


if __name__ == "__main__":
    main()
