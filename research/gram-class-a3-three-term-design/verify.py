"""Exact three-term Gram-class design on the A_3 line system.

Model (the price rule of DreamingOfClouds' p104-duality-ceiling-flag-note,
section 4, specialised to A_n):
  V = {x in Q^(n+1) : sum_i x_i = 0},  Pi = I - J/(n+1) the orthogonal
  projector onto V.  The A_n lines are the pairs (i,j), i < j; the line (i,j)
  is orthogonal to x iff x_i = x_j, and the even-inner-product mask is N = I,
  so a term (u,w) with u,w in V has price rank_F2 N[S,T] = |S cap T| where
  Sep(x) = {(i,j) : x_i != x_j}.  A Gram-class design is Pi = sum_k u_k w_k^T.

This verifier checks, exactly over the rationals:
  1. the written three-term A_3 design sums to Pi_4;
  2. its three prices are 3, 3, 2, total 8;
  3. the natural dual-basis A_3 design sums to Pi_4 and costs 15;
  4. a two-term A_2 design sums to Pi_3 and costs 4 (the predecessor's value,
     reproduced as a control, not claimed as new);
  5. exhaustive enumeration of the declared finite family: every three-term
     design whose U columns are the canonical primitive representatives of the
     14 distinct equality patterns with entries in [-3,3] (1812 designs total)
     has cost at least 8, and the written design is one of the minimisers.
Rejection controls: perturbing one design entry breaks the projector identity,
and a zero carrier does not produce a design.
"""

import hashlib
import json
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

N3 = 4  # A_3 has 4 coordinates and 6 lines


def projector(n):
    return [[Fraction(int(i == j)) - Fraction(1, n) for j in range(n)]
            for i in range(n)]


def seps(x):
    n = len(x)
    return frozenset((i, j) for i in range(n) for j in range(i + 1, n)
                     if x[i] != x[j])


def price(u, w):
    return len(seps(u) & seps(w))


def design_matrix(terms, n):
    return [[sum(u[i] * w[j] for u, w in terms) for j in range(n)]
            for i in range(n)]


def same(a, b):
    return all(a[i][j] == b[i][j] for i in range(len(a)) for j in range(len(a)))


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def det(a):
    n = len(a)
    a = [[Fraction(x) for x in row] for row in a]
    d = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if a[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            a[c], a[p] = a[p], a[c]
            d = -d
        d *= a[c][c]
        pv = a[c][c]
        for r in range(c + 1, n):
            if a[r][c] != 0:
                f = a[r][c] / pv
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return d


def inverse(a):
    n = len(a)
    m = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(n)]
         for i, row in enumerate(a)]
    for c in range(n):
        p = next(r for r in range(c, n) if m[r][c] != 0)
        m[c], m[p] = m[p], m[c]
        pv = m[c][c]
        m[c] = [x / pv for x in m[c]]
        for r in range(n):
            if r != c and m[r][c] != 0:
                f = m[r][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [row[n:] for row in m]


def solve_design(combo):
    """Return the unique W with Pi = U W^T for an N x m full-rank U."""
    n = N3
    m = len(combo)
    u = [[Fraction(combo[k][i]) for k in range(m)] for i in range(n)]
    pi = projector(n)
    utu = [[sum(u[a][i] * u[a][j] for a in range(n)) for j in range(m)]
           for i in range(m)]
    if det(utu) == 0:
        return None
    inv = inverse(utu)
    # W = Pi U (U^T U)^-1
    pu = [[sum(pi[i][a] * u[a][k] for a in range(n)) for k in range(m)]
          for i in range(n)]
    w = [[sum(pu[i][a] * inv[a][k] for a in range(m)) for k in range(m)]
         for i in range(n)]
    terms = [(combo[k], [w[i][k] for i in range(n)]) for k in range(m)]
    if not same(design_matrix(terms, n), pi):
        return None
    return w


def candidate_vectors(n, bound):
    """Canonical primitive representative of each equality pattern."""
    reps = {}
    for v in product(range(-bound, bound + 1), repeat=n):
        if sum(v) != 0 or all(x == 0 for x in v):
            continue
        g = 0
        for x in v:
            g = __import__("math").gcd(g, abs(x))
        if g > 1:
            continue
        first = next(x for x in v if x != 0)
        if first < 0:
            continue
        reps.setdefault(seps(v), tuple(v))
    return sorted(reps.values())


def enumerate_family(bound=3):
    vecs = candidate_vectors(N3, bound)
    best = None
    witness = None
    designs = 0
    for combo in product(vecs, repeat=3):
        w = solve_design(combo)
        if w is None:
            continue
        designs += 1
        terms = [(combo[k], [w[i][k] for i in range(N3)]) for k in range(3)]
        cost = sum(price(u, ww) for u, ww in terms)
        if best is None or cost < best:
            best, witness = cost, (combo, w)
    return len(vecs), designs, best, witness


def main():
    check = {}

    # 1-2. The written A_3 design.
    a3 = [
        ((Fraction(0), Fraction(0), Fraction(1), Fraction(-1)),
         (Fraction(-1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2))),
        ((Fraction(0), Fraction(1), Fraction(-1), Fraction(0)),
         (Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2), Fraction(-1, 2))),
        ((Fraction(1), Fraction(-1), Fraction(1), Fraction(-1)),
         (Fraction(3, 4), Fraction(-1, 4), Fraction(-1, 4), Fraction(-1, 4))),
    ]
    pi4 = projector(4)
    require(same(design_matrix(a3, 4), pi4), "A_3 design does not sum to Pi_4")
    prices = [price(u, w) for u, w in a3]
    require(prices == [3, 3, 2], "A_3 prices changed: %r" % (prices,))
    require(sum(prices) == 8, "A_3 total price is not 8")
    check["a3_design"] = {"prices": prices, "total": sum(prices)}

    # 3. The natural dual-basis design u_k = e_k - e_4, w_k the dual basis.
    dual = []
    for k in range(3):
        u = [Fraction(int(i == k)) - Fraction(int(i == 3)) for i in range(4)]
        w = [Fraction(int(i == k)) - Fraction(1, 4) for i in range(4)]
        dual.append((tuple(u), tuple(w)))
    require(same(design_matrix(dual, 4), pi4), "dual-basis design is not exact")
    dual_prices = [price(u, w) for u, w in dual]
    require(dual_prices == [3, 3, 3], "dual-basis prices changed: %r" % (dual_prices,))
    check["dual_basis"] = {"prices": dual_prices, "total": sum(dual_prices)}
    require(sum(prices) < sum(dual_prices), "written design does not improve 9")

    # 4. A_2 control: the predecessor's Gram value 4, reproduced.
    a2 = [
        ((Fraction(0), Fraction(1), Fraction(-1)),
         (Fraction(1), Fraction(0), Fraction(-1))),
        ((Fraction(1), Fraction(-2), Fraction(1)),
         (Fraction(2, 3), Fraction(-1, 3), Fraction(-1, 3))),
    ]
    require(same(design_matrix(a2, 3), projector(3)), "A_2 control is not exact")
    a2_prices = [price(u, w) for u, w in a2]
    require(sum(a2_prices) == 4, "A_2 control is not 4: %r" % (a2_prices,))
    check["a2_control"] = {"prices": a2_prices, "total": sum(a2_prices)}

    # 5. Declared finite family.
    nvec, designs, best, witness = enumerate_family(3)
    require(nvec == 14, "candidate patterns changed: %d" % nvec)
    require(designs == 1812, "design count changed: %d" % designs)
    require(best == 8, "finite-family minimum changed: %r" % (best,))
    check["family"] = {"patterns": nvec, "designs": designs, "minimum": best}
    wu, ww = witness
    require([price(wu[k], [ww[i][k] for i in range(4)]) for k in range(3)]
            == [3, 3, 2], "family minimiser prices changed")

    # Rejection controls.
    bad = [list(t) for t in a3]
    bad[0] = (bad[0][0], (bad[0][1][0] + Fraction(1, 2),) + bad[0][1][1:])
    require(not same(design_matrix(bad, 4), pi4),
            "perturbed design still equals the projector")
    zero = [(tuple([Fraction(0)] * 4), a3[0][1])] + a3[1:]
    require(not same(design_matrix(zero, 4), pi4),
            "zero-carrier control still equals the projector")
    require(det([[Fraction(x) for x in v] for v in (a3[0][0], a3[1][0], a3[2][0])]) != 0,
            "written U is not full rank")
    check["controls"] = ["perturbed_entry", "zero_carrier", "u_full_rank"]

    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    receipt = {"status": "PASS_GRAM_CLASS_A3_THREE_TERM_DESIGN", "checks": check,
               "sources_sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
