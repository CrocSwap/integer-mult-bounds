#!/usr/bin/env python3
"""Exact verifier: the weighted star program of #6933 has ceiling 5/6 on P104.

Standard library only.  Every printed PASS line is one checked claim; any
mismatch exits non-zero.  Fractions only, no floating point decisions.
"""

import json
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
DATA = REPO / "research/p104-port-window-haemers/data/ports_p104.json"

FAILS = []


def check(name, ok, detail=""):
    if not ok:
        FAILS.append(name)
        print("FAIL " + name + ("  " + detail if detail else ""))
    else:
        print("PASS " + name + ("  " + detail if detail else ""))


def dot(a, b):
    return (a & b).bit_count() & 1


def main():
    ports = json.loads(DATA.read_text())["ports"]
    n = len(ports)
    check("ports.distinct", len(set(ports)) == n == 104, "n=%d" % n)
    check("ports.nonzero_odd_weight",
          all(p > 0 and p.bit_count() % 2 == 1 for p in ports))
    check("ports.weight_3_mod_4",
          all(p.bit_count() % 4 == 3 for p in ports))

    orth = [[dot(ports[i], ports[j]) == 0 for j in range(n)] for i in range(n)]

    # --- orthogonal 8-sets -------------------------------------------------
    sets = []
    cur = []

    def dfs(start):
        if len(cur) == 8:
            sets.append(tuple(cur))
            return
        for j in range(start, n):
            if all(orth[i][j] for i in cur):
                cur.append(j)
                dfs(j + 1)
                cur.pop()

    dfs(0)
    check("orth8.count", len(sets) == 1728, "found %d" % len(sets))

    # --- per-set structure: K + v orthonormal, edge graph, type -------------
    types = Counter()
    per_type_sets = defaultdict(list)
    deg_of_set = {}
    edge_ok = True
    deg_pos = True
    for K in sets:
        Kset = set(K)
        v = 0x1FF          # the all-ones vector of F_2^9, not the integer 1
        for c in K:
            v ^= ports[c]
        if dot(v, v) != 1 or any(dot(v, ports[c]) for c in K):
            edge_ok = False
        deg = Counter()
        E = 0
        pairs = set()
        for t in range(n):
            if t in Kset:
                continue
            A = [c for c in K if dot(ports[t], ports[c]) == 1]
            eps = dot(ports[t], v)
            if (len(A) + eps) % 2 != 1:      # |A| + eps = w(t) mod 2 = 1
                edge_ok = False
            if len(A) == 2:
                E += 1
                pairs.add(tuple(A))
                deg[A[0]] += 1
                deg[A[1]] += 1
        if len(pairs) != E:                   # (H1): distinct edge ports
            edge_ok = False
        ds = tuple(sorted(deg[c] for c in K))
        if min(ds) < 1:
            deg_pos = False
        types[(E, ds)] += 1
        per_type_sets[(E, ds)].append(K)
        deg_of_set[K] = (E, ds, deg)

    check("orth8.orthonormal_basis_and_distinct_pairs", edge_ok)
    check("orth8.every_vertex_positive_degree", deg_pos)
    expect = {
        (22, (5, 5, 5, 5, 6, 6, 6, 6)): 960,
        (22, (5, 5, 5, 5, 5, 6, 6, 7)): 384,
        (21, (5, 5, 5, 5, 5, 5, 6, 6)): 384,
    }
    check("types.census", dict(types) == expect, str(dict(types)))

    # --- the ratio of #6933 Theorem 3 --------------------------------------
    def ratio(E, deg, a):
        mu = sum(1 + a[c] for c in deg)
        rho = F(E) - sum(F(deg[c]) * a[c] for c in deg)
        return (F(E) - mu) / (mu + rho)

    def caps(deg):
        return {c: F(2, deg[c] - 2) for c in deg}

    edge_lists = {}

    def edge_list(K):
        if K not in edge_lists:
            Kset = set(K)
            el = []
            for t in range(n):
                if t in Kset:
                    continue
                A = [c for c in K if dot(ports[t], ports[c]) == 1]
                if len(A) == 2:
                    el.append((A[0], A[1]))
            edge_lists[K] = el
        return edge_lists[K]

    # 1) the three recorded P104 values of #6933 reproduce at their weights
    recorded = {
        (22, (5, 5, 5, 5, 6, 6, 6, 6)): (F(1, 2), F(5, 6)),
        (22, (5, 5, 5, 5, 5, 6, 6, 7)): (F(2, 5), F(101, 126)),
        (21, (5, 5, 5, 5, 5, 5, 6, 6)): (F(1, 2), F(3, 4)),
    }
    for key, (w7, want) in recorded.items():
        K = per_type_sets[key][0]
        E, ds, deg = deg_of_set[K]
        a = {c: (w7 if deg[c] == 7 else F(1, 2)) for c in deg}
        got = ratio(E, deg, a)
        check("compat.value_%s" % (ds,), got == want, "ratio %s" % got)

    # --- the universal multiplier certificate ------------------------------
    #   w_c = 5 d_c - 11 ;  lam = 14/5 on every edge ;
    #   mu_c = ((11/5) d_c - 11) / (d_c - 2)  (>= 0 for d_c >= 5, tight d in {5,6})
    #   coefficient identity  d_c lam + mu_c (d_c - 2) = w_c
    #   cost  (19/5) E + 2 sum_c mu_c  <=  88
    lam = F(14, 5)
    maxcost = F(0)
    worst = None
    ident_ok = True
    tight_deg = set()
    for K in sets:
        E, ds, deg = deg_of_set[K]
        cost = F(19, 5) * E
        for c in deg:
            mu = ((F(11, 5) * deg[c] - 11) / (deg[c] - 2))
            if mu < 0:
                ident_ok = False
            if deg[c] * lam + mu * (deg[c] - 2) != 5 * deg[c] - 11:
                ident_ok = False
            if deg[c] in (5, 6):
                tight_deg.add(deg[c])
            cost += 2 * mu
        if cost > maxcost:
            maxcost, worst = cost, (E, ds)
        if cost > 88:
            ident_ok = False
    check("cert.multiplier_coefficient_identity", ident_ok)
    check("cert.uniform_cost_le_88", maxcost <= 88,
          "max (19/5)E + 2 sum mu = %s at %s" % (maxcost, worst))
    check("cert.only_degrees_5_6_tight", tight_deg == {5, 6})

    # --- the ratio is below 5/6 for every admissible weight vector ---------
    # exact battery: a = 1/2, a = 0, vertex corners of the cap box, and
    # random repaired draws, on every orthogonal 8-set.
    rng = random.Random(1111)
    viol = 0
    tested = 0
    strict_ok = True
    for K in sets:
        E, ds, deg = deg_of_set[K]
        el = edge_list(K)
        cap = caps(deg)
        candidates = [{c: F(0) for c in deg}, {c: cap[c] for c in deg}]
        for c in deg:                       # single-vertex corners
            a = {d: F(0) for d in deg}
            a[c] = cap[c]
            candidates.append(a)
        for _ in range(6):                  # repaired random draws
            a = {}
            for c in deg:
                a[c] = F(rng.randrange(0, 21), 20) * cap[c]
            for _ in range(40):
                bad = [(c, d) for c, d in el if a[c] + a[d] > 1]
                if not bad:
                    break
                for c, d in bad:
                    a[c] = a[d] = (a[c] + a[d]) / 2
            candidates.append(a)
        for a in candidates:
            if any(a[c] < 0 or a[c] * (deg[c] - 2) > 2 for c in deg):
                continue
            if any(a[c] + a[d] > 1 for c, d in el):
                continue
            tested += 1
            f = ratio(E, deg, a)
            if f > F(5, 6):
                viol += 1
            if f == F(5, 6) and ds == (5, 5, 5, 5, 6, 6, 6, 6) and a != half:
                strict_ok = False
    check("bound.no_violation_on_battery", viol == 0,
          "%d feasible weight vectors tested" % tested)
    check("bound.equality_only_at_half_on_principal_type", strict_ok)

    # --- equality is attained, so 5/6 is the exact supremum ---------------
    K = per_type_sets[(22, (5, 5, 5, 5, 6, 6, 6, 6))][0]
    E, ds, deg = deg_of_set[K]
    el = edge_list(K)
    a = {c: F(1, 2) for c in deg}
    check("sharp.attained_at_half",
          all(a[c] * (deg[c] - 2) <= 2 for c in deg) and
          all(a[c] + a[d] <= 1 for c, d in el) and
          ratio(E, deg, a) == F(5, 6),
          "ratio %s" % ratio(E, deg, a))

    # --- rigidity: every degree-5 vertex has a degree-6 neighbour ---------
    # This is the step that turns "all edges tight" into "all a_c = 1/2":
    # a degree-5 vertex has 5 neighbours but only 3 other degree-5 vertices.
    rigid = True
    for K in per_type_sets[(22, (5, 5, 5, 5, 6, 6, 6, 6))]:
        E, ds, deg = deg_of_set[K]
        nbr = defaultdict(set)
        for c, d in edge_list(K):
            nbr[c].add(d)
            nbr[d].add(c)
        for c in deg:
            if deg[c] == 5 and not any(deg[d] == 6 for d in nbr[c]):
                rigid = False
    check("rigid.degree5_vertex_has_degree6_neighbour", rigid)

    # --- controls ---------------------------------------------------------
    # (a) the hypothesis (W2) is needed: a_c = 3/5 at a degree-6 vertex
    K = per_type_sets[(22, (5, 5, 5, 5, 6, 6, 6, 6))][0]
    E, ds, deg = deg_of_set[K]
    a = {c: F(1, 2) for c in deg}
    big = next(c for c in deg if deg[c] == 6)
    a[big] = F(3, 5)
    violated = a[big] * (deg[big] - 2) > 2
    check("control.w2_needed", violated and ratio(E, deg, a) > F(5, 6),
          "ratio %s with a_c=3/5" % ratio(E, deg, a))

    # (b) a mutant multiplier must fail the coefficient identity
    lam_bad = F(13, 5)
    mutant_breaks = False
    for c in deg:
        mu = ((F(11, 5) * deg[c] - 11) / (deg[c] - 2))
        if deg[c] * lam_bad + mu * (deg[c] - 2) != 5 * deg[c] - 11:
            mutant_breaks = True
    check("control.mutant_multiplier_detected", mutant_breaks)

    # (c) a mutated census count must be detected
    wrong = dict(expect)
    wrong[(22, (5, 5, 5, 5, 6, 6, 6, 6))] = 959
    check("control.mutated_census_detected", wrong != dict(types))

    if FAILS:
        print("FAILED_P104_STAR_WEIGHT_OPTIMUM  %d failing checks: %s"
              % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("PASS_P104_STAR_WEIGHT_OPTIMUM")
    return 0


if __name__ == "__main__":
    sys.exit(main())
