#!/usr/bin/env python3
"""Independent standard-library exact checker; works with and without -O."""

from __future__ import annotations

import argparse
import atexit
import hashlib
import itertools
import json
import random
import sys
import tempfile
from math import isqrt
from pathlib import Path

sys.dont_write_bytecode = True
_cache = tempfile.TemporaryDirectory(prefix="ring-review-")
sys.pycache_prefix = str(Path(_cache.name) / "required-absent")
atexit.register(_cache.cleanup)
from matching import add, forward, hadamard, inverse, match, norm2, sub, turn


def require(ok, label):
    if not ok:
        raise RuntimeError(label)


COUNTS = {"half_grid_points": 0, "ring_pairs": 0, "gaussian_pairs": 0,
          "large_gaussian_pairs": 0, "negative_controls": 0}
SCALE = 1 << 128
BETA_LOWER_SCALED = isqrt(19 * SCALE**2) - isqrt(13 * SCALE**2) - 1


def check_match(z):
    w = match(z)
    require(w[0] % 2 == 1 and w[1] % 2 == 1, "half-grid closure")
    require(norm2(sub(w, z)) == 4, "unit neighbor")
    require(match(w) == z, "matching involution")
    require(match(turn(z)) == turn(w), "quarter-turn equivariance")
    require(((sum(w) - sum(z)) // 2) % 2 == 1, "bipartite color flip")
    r = max(map(abs, z))
    a = r if r % 4 == 1 else r - 2
    require(max(map(abs, w)) in (a, a + 2), "paired rings")
    COUNTS["half_grid_points"] += 1


def check_radial(n, m):
    if {n, m} == {13, 19}:
        return
    lo, hi = sorted((n, m))
    upper = isqrt(hi * SCALE**2) + 1 - isqrt(lo * SCALE**2)
    require(upper <= BETA_LOWER_SCALED, "exact radical-interval radial bound")


def check_pair(pair, large=False):
    u, v = pair
    out = forward(pair)
    require(add(*out) == add(u, v), "exact sum")
    require(forward(out) == (v, u), "F squared = swap")
    require(forward((v, u)) == (out[1], out[0]), "wire-swap equivariance")
    require(inverse(out) == pair and forward(inverse(pair)) == pair, "inverse")
    require(forward((turn(u), turn(v))) == tuple(map(turn, out)), "Gaussian i equivariance")
    s, jd = add(u, v), turn(sub(u, v))
    err = (sub((2*out[0][0], 2*out[0][1]), add(s, jd)),
           sub((2*out[1][0], 2*out[1][1]), sub(s, jd)))
    mixed = (s[0] - s[1]) % 2
    require(norm2(err[0]) == 2*mixed and norm2(err[1]) == 2*mixed,
            "exact individual and pair error")
    check_radial(norm2(u) + norm2(v), sum(map(norm2, out)))
    COUNTS["large_gaussian_pairs" if large else "gaussian_pairs"] += 1


def ring(radius):
    points = set()
    for x in range(-radius, radius + 1, 2):
        points.update(((x, radius), (x, -radius), (radius, x), (-radius, x)))
    return points


def check_arcs(m):
    a, b = 4*m + 1, 4*m + 3
    inner, outer = ring(a), ring(b)
    require(len(inner) == 4*a and len(outer) == 4*b, "ring cardinalities")
    connectors_inner = {turn((a, a), q) for q in range(4)}
    connectors_outer = {turn((b, a), q) for q in range(4)}
    ia = [(x, a) for x in range(a - 2, -a, -2)]
    oa = [(x, b) for x in range(b, -a, -2)]
    require(len(ia) == 4*m and len(oa) == 4*m + 2, "arc cardinalities")
    for source, connectors, canonical in ((inner, connectors_inner, ia),
                                           (outer, connectors_outer, oa)):
        arcs = [{turn(z, q) for z in canonical} for q in range(4)]
        union = set().union(*arcs)
        require(len(union) == 4*len(canonical), "rotated arcs are disjoint")
        require(union == source - connectors, "arcs cover all remaining points")
        for arc in arcs:
            require(all(match(z) in arc for z in arc), "arc matching stays in arc")
    COUNTS["ring_pairs"] += 1


def expect_failure(function, label):
    try:
        function()
    except (RuntimeError, ValueError, ArithmeticError):
        COUNTS["negative_controls"] += 1
        return
    raise RuntimeError("negative control survived: " + label)


def controls():
    # A diagonal connector is no longer a unit neighbor and raises the error.
    def diagonal(z):
        return (3, 3) if z == (1, 1) else match(z)
    expect_failure(lambda: require(norm2(sub(diagonal((1,1)), (1,1))) == 4,
                                   "diagonal connector"), "diagonal connector")
    # Reversing the mate choice on only the first outer-arc point breaks M^2.
    def bad_arc(z):
        return (5, 3) if z == (3, 3) else match(z)
    expect_failure(lambda: require(bad_arc(bad_arc((3,3))) == (3,3),
                                   "bad arc involution"), "arc pairing")
    # This is an actual symmetric unit-neighbor involution, but one 4-cycle
    # flip on the top-right outer corner destroys quarter-turn symmetry.
    patch = {(3,3):(3,1), (3,1):(3,3), (1,3):(1,1), (1,1):(1,3)}
    def asymmetric(z):
        return patch.get(z, match(z))
    expect_failure(lambda: require(asymmetric(turn((1,1))) == turn(asymmetric((1,1))),
                                   "broken quarter symmetry"), "quarter symmetry")
    expect_failure(lambda: require(forward(forward(((0,0),(0,1)), asymmetric), asymmetric)
                                   == ((0,1),(0,0)), "asymmetric F square"),
                   "asymmetric F square")
    # Accepting a central half-grid point without a unit move breaks parity.
    expect_failure(lambda: forward(((1,0),(0,0)), lambda z: z), "missing parity flip")
    # Exact-map witnesses are sensitive to connector direction, not only norms.
    expect_failure(lambda: require(forward(((0,-2),(0,3))) == ((-3,0),(3,1)),
                                   "wrong attaining connector"), "attaining direction")
    conj = lambda z: (z[0], -z[1])
    p = ((1,0),(0,0))
    kfk = tuple(map(conj, forward(tuple(map(conj, p)))))
    expect_failure(lambda: require(kfk == inverse(p), "conjugation inverse"),
                   "inverse by conjugation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for z in itertools.product(range(-257, 258, 2), repeat=2):
        check_match(z)
    for m in range(129):
        check_arcs(m)
    for coords in itertools.product(range(-7, 8), repeat=4):
        check_pair((coords[:2], coords[2:]))
    rng = random.Random(2026111312)
    for bits in (64, 127, 256, 1024, 4096):
        for _ in range(64):
            coords = tuple(rng.getrandbits(bits) * rng.choice((-1,1)) for _ in range(4))
            check_pair((coords[:2], coords[2:]), large=True)
        # Very large corners, connector neighbors and arc-end points, all signs.
        for m in (1 << bits, (1 << bits) + 1):
            a = 4*m + 1
            for z in ((a,a),(a+2,a),(a+2,a+2),(a,a+2),(-a+2,a+2),(a-2,a)):
                for q in range(4):
                    check_match(turn(z,q))
    witness = ((0,-2),(0,3))
    require(forward(witness) == ((3,1),(-3,0)), "attaining witness output")
    require((sum(map(norm2, witness)), sum(map(norm2, forward(witness)))) == (13,19),
            "attaining witness radii")
    controls()
    result = {"status":"PASS", "counts":COUNTS,
              "radical_interval_bits":128,
              "witness":{"input":witness,"output":forward(witness),"norm_squares":[13,19]},
              "source_sha256":{name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                                 for name in ("matching.py","check.py")},
              "scope":"mathematical integer model; no physical/caller claim; no arbitrary-map reduction"}
    if args.write:
        Path(__file__).with_name("RESULT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
