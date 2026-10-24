#!/usr/bin/env python3
"""Structure of the 24 five-rectangle decompositions of J - I_5 over F2 (#4598 open question 1).

#4598 (petalas) counts 2,880 complete passing headers for five orthogonal binary requests in dimension six, via
24 unordered decompositions J - I_5 = sum of five rectangles 1_S 1_T^T with S, T disjoint and nonempty, over F2
(each giving 5! ordered headers). Its open question 1 asks to explain the 24, starting with coordinate-permutation and
transposition orbits. This verifier enumerates the decompositions independently and proves the classification:

  24 = 2 + 10 + 12 orbits under S5 x <transpose> (simultaneous coordinate permutation, (S,T) -> (T,S)):
  * stars (2): {i} x (V - i) for all i (row star) and its transpose (column star);
  * mixed (10): for a centre c, {c} x (V - c) together with (V - {c,y}) x {c,y} for the four y != c, and transposes;
    S5-orbits of size 5 (one per centre). Column c is covered 1 + 3 times, so these sum to J - I only mod 2;
  * pentagons (12): the five edges {u,v} of an undirected Hamiltonian 5-cycle, each with T = the two cycle
    neighbours of the edge outside it; one per undirected 5-cycle (4!/2 = 12), stabiliser D5 of order 10, closed
    under transposition. These sum to J - I over the integers (the #4598 hand counterexample is one of them).
So the 22 non-star subsets are 10 characteristic-2 "mixed" ones and 12 integral pentagons.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from itertools import combinations, permutations
import json
import sys

V = range(5)
E = sum(1 << (5 * i + j) for i in V for j in V if i != j)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def rect(s, t):
    return sum(1 << (5 * i + j) for i in V if s >> i & 1 for j in V if t >> j & 1)


def mask(xs):
    return sum(1 << x for x in xs)


def decompositions():
    rects = [(s, t) for s in range(1, 32) for t in range(1, 32) if s & t == 0]
    need(len(rects) == 180, "180 nonzero disjoint-support rectangles")
    m = [rect(s, t) for s, t in rects]
    pairs = {}
    for a, b in combinations(range(180), 2):
        pairs.setdefault(m[a] ^ m[b], []).append((a, b))
    sols = set()
    for c, d, e in combinations(range(180), 3):
        for a, b in pairs.get(E ^ m[c] ^ m[d] ^ m[e], ()):
            if b < c:
                sols.add(frozenset(rects[i] for i in (a, b, c, d, e)))
    return sols


def act(sol, p, transpose):
    f = lambda x: mask(p[i] for i in V if x >> i & 1)
    return frozenset((f(t), f(s)) if transpose else (f(s), f(t)) for s, t in sol)


def integer_sum(sol):
    return Counter((i, j) for s, t in sol for i in V if s >> i & 1 for j in V if t >> j & 1)


def main():
    sols = decompositions()
    need(len(sols) == 24, "24 decompositions (#4598)")
    full = mask(V)
    stars = {frozenset((1 << i, full ^ (1 << i)) for i in V), frozenset((full ^ (1 << i), 1 << i) for i in V)}
    mixed = set()
    for c in V:
        base = {(1 << c, full ^ (1 << c))} | {(full ^ mask((c, y)), mask((c, y))) for y in V if y != c}
        mixed |= {frozenset(base), frozenset((t, s) for s, t in base)}
    pentagons = set()
    for order in permutations(V):
        if order[0] != 0:
            continue
        nb = {order[k]: (order[k - 1], order[(k + 1) % 5]) for k in range(5)}
        sol = set()
        for k in range(5):
            u, v = order[k], order[(k + 1) % 5]
            outside = {x for x in nb[u] + nb[v] if x not in (u, v)}
            sol.add((mask((u, v)), mask(outside)))
        pentagons.add(frozenset(sol))
    need(len(stars) == 2 and len(mixed) == 10 and len(pentagons) == 12, "family sizes 2 + 10 + 12")
    need(stars | mixed | pentagons == sols and not (stars & mixed or stars & pentagons or mixed & pentagons),
         "the three families partition the 24")
    orbits, seen = [], set()
    for s in sorted(sols, key=sorted):
        if s not in seen:
            orb = {act(s, p, tr) for p in permutations(V) for tr in (0, 1)}
            seen |= orb
            orbits.append(orb)
    need(sorted(len(o) for o in orbits) == [2, 10, 12] and {frozenset(o) for o in orbits} ==
         {frozenset(stars), frozenset(mixed), frozenset(pentagons)}, "orbits are exactly the three families")
    ideal = Counter({(i, j): 1 for i in V for j in V if i != j})
    need(all(integer_sum(s) == ideal for s in stars | pentagons), "stars and pentagons sum to J - I over Z")
    need(all(integer_sum(s) != ideal for s in mixed), "mixed decompositions sum to J - I only mod 2")
    hand = frozenset({(mask((0, 1)), mask((2, 3))), (mask((1, 2)), mask((0, 4))), (mask((0, 3)), mask((1, 4))),
                      (mask((2, 4)), mask((1, 3))), (mask((3, 4)), mask((0, 2)))})
    need(hand in pentagons, "#4598's hand counterexample is a pentagon")
    print(json.dumps({"status": "PASS_FIVE_REQUEST_DECOMPOSITION_STRUCTURE", "decompositions": 24,
                      "orbits_S5_x_transpose": {"stars": 2, "mixed_char2": 10, "pentagons": 12},
                      "headers": {"stars": 240, "mixed": 1200, "pentagons": 1440, "total": 2880},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
