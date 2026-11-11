#!/usr/bin/env python3
"""Exact finite corroboration of the paired-root three-cycle theorem."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(type(n) is int and 1 <= n <= 8, "dimension outside 1..8")
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    require(a and a[0] and all(len(r) == len(a[0]) for r in a), "bad matrix")
    return [list(c) for c in zip(*a)]


def multiply(a, b):
    require(a and b and len(a[0]) == len(b), "bad product dimensions")
    bt = transpose(b)
    return [[sum((x * y for x, y in zip(r, c)), F(0)) for c in bt] for r in a]


def inverse(a):
    n = len(a)
    require(1 <= n <= 8 and all(len(r) == n for r in a), "bad square matrix")
    w = [list(r) + e for r, e in zip(a, identity(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if w[k][j]), None)
        require(k is not None, "singular matrix")
        w[j], w[k] = w[k], w[j]
        w[j] = [x / w[j][j] for x in w[j]]
        for k in range(n):
            if k != j:
                scale = w[k][j]
                w[k] = [x - scale * y for x, y in zip(w[k], w[j])]
    require([r[:n] for r in w] == identity(n), "inverse elimination failed")
    return [r[n:] for r in w]


def roots(n, edges):
    identity(n)
    require(edges and len(edges) <= 28 and len(set(edges)) == len(edges), "bad edges")
    require(all(type(i) is int and type(j) is int and 0 <= i < j < n
                for i, j in edges), "bad edge endpoints")
    rows = []
    for i, j in edges:
        for sign in (1, -1):
            row = [F(0)] * n
            row[i], row[j] = F(1), F(sign)
            rows.append(row)
    return rows


def cycle(n, t, s, u):
    require(n >= 3, "cycle needs three coordinates")
    require(all(type(x) in (int, F) and abs(x) <= 8 for x in (t, s, u)),
            "bad cycle coefficient")
    t, s, u = F(t), F(s), F(u)
    m = identity(n)
    for a, b, x in ((0, 1, t), (1, 2, s), (2, 0, u)):
        h = identity(n)
        h[a][b] = x
        m = multiply(m, h)
    dual = transpose(inverse(m))
    closed_m, closed_q = identity(n), identity(n)
    closed_m[:3] = [r + [F(0)] * (n - 3) for r in
                      ([1 + t*s*u, t, t*s], [s*u, 1, s], [u, 0, 1])]
    closed_q[:3] = [r + [F(0)] * (n - 3) for r in
                      ([1, 0, -u], [-t, 1, t*u], [0, -s, 1])]
    require(m == closed_m and dual == closed_q, "closed cycle formula mismatch")
    return m, dual


def factors(n, edges, coeffs):
    r = roots(n, edges)
    m, dual = cycle(n, *coeffs)
    p, q = multiply(r, m), multiply(r, dual)
    require(multiply(p, transpose(q)) == multiply(r, transpose(r)), "wrong Gram endpoint")
    return r, p, q


def star_witnesses(n, edges, p, q):
    witnesses = []
    for j in range(n):
        chosen = []
        for e, edge in enumerate(edges):
            if j in edge:
                choices = [k for k in (2*e, 2*e+1) if p[k][j] and q[k][j]]
                require(choices, "missing common sign root")
                chosen.append(choices[0])
        witnesses.append(chosen)
    return witnesses


def fitting(r, b):
    v = len(r)
    require(len(b) == v and all(type(row) is int and 0 <= row < 1 << v for row in b),
            "bad binary matrix")
    for i in range(v):
        require(b[i] >> i & 1, "missing diagonal one")
        for j in range(v):
            if i != j and sum(x*y for x, y in zip(r[i], r[j])):
                require(not (b[i] >> j & 1), "forbidden nonorthogonal entry")


def pairings(r):
    v = len(r)
    free = [(i, j) for i in range(v) for j in range(v) if i != j
            and sum(x*y for x, y in zip(r[i], r[j])) == 0]
    require(len(free) <= 6, "complete census limited to six free bits")
    for bits in range(1 << len(free)):
        b = [1 << i for i in range(v)]
        for k, (i, j) in enumerate(free):
            b[i] |= (bits >> k & 1) << j
        yield b


def rank(rows):
    pivots = {}
    for row in rows:
        for _ in range(57):
            if not row:
                break
            j = row.bit_length() - 1
            if j not in pivots:
                pivots[j] = row
                break
            row ^= pivots[j]
        else:
            raise ValueError("rank iteration bound exhausted")
    return len(pivots)


def span_rank(rows):
    require(len(rows) <= 6, "span oracle limited to six rows")
    space = {0}
    for row in rows:
        space |= {x ^ row for x in space}
    require(len(space).bit_count() == 1, "span size is not a power of two")
    return len(space).bit_length() - 1


def bill(p, q, b, oracle=False):
    costs = []
    for j in range(len(p[0])):
        cols = sum(1 << k for k in range(len(q)) if q[k][j])
        rows = [b[k] & cols for k in range(len(p)) if p[k][j]]
        cost = rank(rows)
        if oracle:
            require(cost == span_rank(rows), "rank and span disagree")
        costs.append(cost)
    return costs


def check_minors(r, b, witnesses):
    count = 0
    for chosen in witnesses:
        for i in chosen:
            for j in chosen:
                require((b[i] >> j & 1) == (i == j), "forced minor is not identity")
                count += 1
    return count


def small_census():
    alphabet = tuple(map(F, (-2, -1, 0, 1, 2))) + (F(-1, 2), F(1, 2))
    all_edges = list(combinations(range(3), 2))
    totals = dict(factorizations=0, common_pairing_bills=0, identity_entries=0,
                  span_comparisons=0, excluded_parameter_triples=0)
    for coeffs in product(alphabet, repeat=3):
        if coeffs[0]*coeffs[1]*coeffs[2] in (-1, 1):
            totals["excluded_parameter_triples"] += 1
            continue
        for mask in range(1, 8):
            edges = [e for k, e in enumerate(all_edges) if mask >> k & 1]
            r, p, q = factors(3, edges, coeffs)
            witnesses = star_witnesses(3, edges, p, q)
            totals["factorizations"] += 1
            for b in pairings(r):
                fitting(r, b)
                costs = bill(p, q, b, oracle=True)
                require(all(c >= len(w) for c, w in zip(costs, witnesses)),
                        "term fell below its degree")
                require(sum(costs) >= len(r), "complete bill below root count")
                totals["identity_entries"] += check_minors(r, b, witnesses)
                totals["common_pairing_bills"] += 1
                totals["span_comparisons"] += 3
    return totals


def sampled_pairing(r, seed):
    v = len(r)
    return [sum(1 << j for j in range(v) if i == j or
                (sum(x*y for x, y in zip(r[i], r[j])) == 0 and
                 ((i+1)*17 + (j+1)*31 + seed*13) % 7 < 3)) for i in range(v)]


def larger_fixtures():
    graphs = [(4, [(0, 1), (1, 2), (2, 3)]),
              (5, [(0, 1), (0, 2), (0, 4), (1, 2), (2, 3), (3, 4)]),
              (8, [(0, 3), (0, 4), (1, 4), (2, 5), (2, 6)]),
              (8, [(0, 1), (0, 2), (1, 2)])]
    triples = [(F(2), F(1), F(1)), (F(-2), F(1), F(1)),
               (F(1, 2), F(1, 2), F(1, 2)), (F(0), F(2), F(-1)),
               (F(-2), F(-2), F(2)), (F(1), F(-1, 2), F(1))]
    totals = dict(factorizations=0, common_pairing_bills=0, identity_entries=0)
    first_fixture = None
    for n, edges in graphs:
        for coeffs in triples:
            r, p, q = factors(n, edges, coeffs)
            witnesses = star_witnesses(n, edges, p, q)
            for seed in range(7):
                b = sampled_pairing(r, seed)
                fitting(r, b)
                costs = bill(p, q, b)
                require(all(c >= len(w) for c, w in zip(costs, witnesses)),
                        "large term below degree")
                totals["identity_entries"] += check_minors(r, b, witnesses)
                totals["common_pairing_bills"] += 1
            if n == 5 and coeffs == triples[0]:
                b = [(3 << (2*(i//2))) for i in range(len(r))]
                fitting(r, b)
                first_fixture = bill(p, q, b)
            totals["factorizations"] += 1
    require(first_fixture is not None, "missing actual D5 example")
    totals["actual_D5_edge_block_bill"] = first_fixture
    return totals


def rejected_controls():
    probes = [(1, (1, 1, 1), (0, 2)), (-1, (1, 1, -1), (1, 2))]
    for value, coeffs, edge in probes:
        _, p, q = factors(3, [edge], coeffs)
        require(coeffs[0]*coeffs[1]*coeffs[2] == value, "wrong exceptional fixture")
        require(all(not (p[k][2] and q[k][2]) for k in range(2)),
                "exceptional minor unexpectedly survives")
    rejected = 0
    for mode in range(8):
        try:
            if mode == 0:
                roots(3, [(1, 0)])
            elif mode == 1:
                roots(3, [(0, 1), (0, 1)])
            elif mode == 2:
                cycle(2, 1, 1, 1)
            elif mode == 3:
                cycle(3, 9, 1, 1)
            elif mode == 4:
                inverse([[F(0), F(0)], [F(0), F(0)]])
            elif mode == 5:
                fitting(roots(3, [(0, 1)]), [0, 0])
            elif mode == 6:
                fitting(roots(3, [(0, 1), (1, 2)]), [5, 2, 4, 8])
            else:
                _, p, q = factors(3, [(0, 2)], (1, 1, 1))
                star_witnesses(3, [(0, 2)], p, q)
        except ValueError:
            rejected += 1
    require(rejected == 8, "a rejecting control was accepted")
    return dict(rejected_inputs_and_false_minors=rejected, exceptional_locus_witnesses=2)


def main():
    result = dict(small=small_census(), larger=larger_fixtures(), controls=rejected_controls())
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: sha256((package/name).read_bytes()).hexdigest() for name in names}
    result["status"] = "PASS_DN_THREE_CYCLE_FLOOR"
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
