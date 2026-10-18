"""Exact rational certification that no reported optimal profile raises the nine-stage bit c.

For a local paid profile P the nine-stage profile is 288 P + REM (REM is the idle remainder of the frozen hosting,
read off PR589's hosted audit; PR589's tune/fastc.py checks that this reproduces the pipeline c). The moment
    M_P(a) = sum_d n_d d/(m W) (m/d)^a + 32 m (sum_d n_d)/(10^16 W) m^a,   m = 64, W = 28416,
is strictly increasing in a, and c(P) is its root of M_P = 1. With c0 the base word's published lower endpoint,
a rigorous lower bound M_P(c0) > 1 proves c(P) < c0. The bounds come from the repository's exact engine
(alternating Mercator logarithms, 24-term exponential with geometric tail, outward dyadic rounding).

Usage: certify.py PROFILES.json   (a JSON list of local profiles {rank: count})
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENG = ROOT / 'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py'
spec = importlib.util.spec_from_file_location('pr589_moment', ENG)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

REM = {2: 13920, 4: 14208, 6: 14208, 7: 21312, 42: 288}  # PR589 tune/fastc.py
m, W, T = 64, 28416, 288
BASE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
C0 = Fraction(1733427039589844234749, 10 ** 24)


def nine_stage(local):
    P = {}
    for d, n in local.items():
        P[int(d)] = P.get(int(d), 0) + T * n
    for d, n in REM.items():
        P[d] = P.get(d, 0) + n
    assert m * W - sum(d * n for d, n in P.items()) == 10272, 'rank mass changed'
    return P


def main():
    profiles = json.load(open(sys.argv[1]))
    # control: the base profile's moment brackets 1 at the published endpoint grid
    lo_b, hi_b = M.moment(nine_stage(BASE), m, W, C0, True)
    lo_u, hi_u = M.moment(nine_stage(BASE), m, W, C0 + Fraction(1, 10 ** 24), True)
    assert hi_b < 1 < lo_u, 'base endpoint control failed'
    seen = set()
    worst = None
    out = []
    for local in profiles:
        local = {int(k): v for k, v in local.items() if v}
        key = tuple(sorted(local.items()))
        if key in seen:
            continue
        seen.add(key)
        if local == BASE:
            out.append(dict(profile=local, verdict='base'))
            continue
        lo, hi = M.moment(nine_stage(local), m, W, C0, True)
        ok = lo > 1
        excess = lo - 1
        worst = excess if worst is None or excess < worst else worst
        out.append(dict(profile=local, verdict='c below base' if ok else 'NOT CERTIFIED',
                        moment_minus_one_lower=M.decimal(excess)))
    bad = [r for r in out if r['verdict'] == 'NOT CERTIFIED']
    print(json.dumps(dict(distinct_profiles=len(out), certified_below=sum(r['verdict'] == 'c below base' for r in out),
                          base=sum(r['verdict'] == 'base' for r in out), not_certified=len(bad),
                          smallest_moment_excess=None if worst is None else M.decimal(worst),
                          base_endpoint_control='pass')))
    if bad:
        sys.exit(1)


if __name__ == '__main__':
    main()
