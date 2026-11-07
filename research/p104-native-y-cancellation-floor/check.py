#!/usr/bin/env python3
"""Exact checks for the Y-cancellation arrival floor on P104.  Python 3.12, standard library only.

Run:  python3 -I -B research/p104-native-y-cancellation-floor/check.py
Marker: PASS_P104_NATIVE_Y_CANCELLATION_FLOOR

Input: the 104 ports of research/p104-designer-toolkit-v2/words/5561.json.gz (9-bit integers).
Everything is recomputed from the port list; nothing is read from a word's program.
"""
import gzip
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTS_FILE = HERE.parent / "p104-designer-toolkit-v2" / "words" / "5561.json.gz"


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def dot(a, b):
    return bin(a & b).count("1") & 1


def gf2_rank(vs):
    basis = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


ports = json.loads(gzip.decompress(PORTS_FILE.read_bytes()))["ports"]
n = len(ports)
require(n == 104 and len(set(ports)) == 104 and all(0 < p < 512 for p in ports), "port list shape")
ONES = 511  # the all-ones functional: v . ONES = wt(v) mod 2

# (1) odd weights, hence q_p is not in H_p = q_p^perp
require(all(bin(p).count("1") % 2 == 1 for p in ports), "odd weights")
require(all(dot(p, p) == 1 for p in ports), "q_p not in H_p")
require(all(dot(p, ONES) == 1 for p in ports), "v . 1 = 1 on every port")
print("ports: 104 distinct, all odd weight, q_p . q_p = 1 (q_p outside H_p); GF(2) rank of all ports =", gf2_rank(ports))

# (2) Orth(p): size 48, GF(2) rank 8 (spans H_p), for all ports
sum_pairs = 0
single_total = 0
for i, q in enumerate(ports):
    orth = [v for j, v in enumerate(ports) if j != i and dot(q, v) == 0]
    require(len(orth) == 48, f"|Orth| port {i}")
    require(gf2_rank(orth) == 8, f"rank Orth port {i}")
    require(all(dot(q, v) == 0 for v in orth), "Orth inside H_p")
    oset = frozenset(orth)

    # Hyperplanes of H_p = kernels of functionals a restricted to H_p; a ~ a^q on H_p.
    # Functionals a not in {0, q} give the 255 distinct hyperplanes.
    reps = {}
    for a in range(1, 512):
        if a == q:
            continue
        reps[min(a, a ^ q)] = a
    require(len(reps) == 255, "255 hyperplanes of H_p")
    ker = {k: frozenset(v for v in orth if dot(v, k) == 0) for k in reps}

    # no single hyperplane (hence no single proper subspace) of H_p contains Orth(p)
    singles = [k for k in reps if ker[k] == oset]
    require(not singles, f"a single hyperplane covers Orth port {i}")
    single_total += len(singles)

    # covering pairs, found by brute force over all C(255,2) pairs
    cov = {frozenset((x, y)) for x, y in itertools.combinations(reps, 2) if ker[x] | ker[y] == oset}
    require(len(cov) == 127, f"covering pairs port {i}: {len(cov)}")

    # they are exactly the parity-complementary pairs {a, a^ONES} (as classes mod q)
    cls = lambda a: min(a, a ^ q)
    comp = set()
    for k in reps:
        k2 = cls(k ^ ONES)
        if k2 not in reps:
            # k is the class of the all-ones functional: its partner would be the trivial functional,
            # i.e. all of H_p, which is not a hyperplane (the all-ones hyperplane meets Orth(p) in nothing).
            require(cls(k) == cls(ONES) and not ker[k], "only the all-ones class has no partner")
            continue
        require(k2 != k, "a and a+1 distinct on H_p")
        comp.add(frozenset((k, k2)))
    require(len(comp) == 127, "127 complementary pairs")
    require(cov == comp, f"covering pairs are exactly the complementary ones, port {i}")
    sum_pairs += len(cov)

require(ONES not in ports, "all-ones vector is not a port")
require(sum_pairs == 104 * 127 and single_total == 0, "totals")
print("Orth(p): size 48, GF(2) rank 8 for all 104 ports")
print("covering pairs of hyperplanes of H_p: exactly 127 per port, all parity-complementary {a, a+1}; no single hyperplane covers")
print("PASS_P104_NATIVE_Y_CANCELLATION_FLOOR")
