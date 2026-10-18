"""Independent finite shell/permutation and rational shear checks."""
from fractions import Fraction as Q
from itertools import permutations
from math import isqrt, floor
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import authenticate, need


def run():
    authenticate()
    shell_cases = 0
    for p in range(13):
        s = 2**p
        shell = set()
        for a in range(-s, s + 1):
            q = s*s - a*a
            b = isqrt(q)
            if b*b == q:
                shell.add((a, b))
                shell.add((a, -b))
        need(shell == {(s, 0), (-s, 0), (0, s), (0, -s)}, 'independent dyadic boundary')
        shell_cases += 1
    points = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    sq = lambda z: z[0]**2 + z[1]**2
    contractive = 0
    for output in permutations(points):
        if all(sq(y) <= sq(x) for x, y in zip(points, output)):
            need(all(sq(y) == sq(x) for x, y in zip(points, output)), 'finite shell lemma')
            contractive += 1
    need(contractive == 24, 'complete permutation count')
    # Literal rational arithmetic; do not import primary lift/inverse.
    shear_cases, worst = 0, Q(0)
    rnd = lambda q: floor(q + Q(1, 2))
    for a in range(-31, 32):
        for b in range(-31, 32):
            x = a - rnd(Q(b, 2))
            e1 = Q(x) - a + Q(b, 2)
            y = b + rnd(Q(4*x, 5))
            e2 = Q(y) - b - Q(4*x, 5)
            z = x - rnd(Q(y, 2))
            e3 = Q(z) - x + Q(y, 2)
            ex, ey = Q(z)-Q(3*a-4*b, 5), Q(y)-Q(4*a+3*b, 5)
            need(ex == Q(3, 5)*e1-Q(1, 2)*e2+e3 and
                 ey == Q(4, 5)*e1+e2, 'shear residual identity')
            need(max(abs(e1), abs(e2), abs(e3)) <= Q(1, 2), 'rounding residual')
            need(ex*ex + ey*ey <= Q(153, 80), 'uniform lifted error')
            backx = z + rnd(Q(y, 2))
            backy = y - rnd(Q(4*backx, 5))
            backx += rnd(Q(backy, 2))
            need((backx, backy) == (a, b), 'independent exact inverse')
            worst = max(worst, ex*ex+ey*ey)
            shear_cases += 1
    return dict(status='PASS_INDEPENDENT_PHASE_BOUNDARY', boundary_shells=shell_cases,
                permutations=120, contractive_permutations=contractive,
                rational_shear_cases=shear_cases, max_observed_squared_error=str(worst))


if __name__ == '__main__':
    import json
    need(not sys.argv[1:], 'unknown arguments')
    print(json.dumps(run(), sort_keys=True))
