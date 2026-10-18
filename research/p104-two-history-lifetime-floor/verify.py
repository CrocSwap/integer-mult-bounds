#!/usr/bin/env python3
"""Re-price PR2920's two-history P104 profile under reported lifetime floors.

PR2920 minimizes the transport/ideal-idle moment over (cheap, unit) helper
counts subject to PR2909's endpoint curve and C+U <= 482. Its optimum (0, 208)
has 208 lifetimes. This checker adds C+U >= L for reported floors L and
certifies the new optimizer, its selected moment and its relaxed root, plus the
smallest L at which this two-type screen rejects.

The moment is affine in (C, U): counts enter linearly and idle mass is the
fixed template mass minus the local mass. Three certified `ceiling.relax`
enclosures therefore give exact-interval coefficients; every optimizer is also
re-evaluated directly with `relax` as a control.

Sudarsh Chaturvedi, with substantial Anthropic Claude assistance. Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import subprocess

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SELECTED = Q(67018507072324140917, 40000000000000000000000)
BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
TEMPLATE = (73, 832, 9, 56)          # m, families, stages, centre (PR2675 / PR2920)
MAX_LIFETIMES = 482                  # idle-capacity bound stated by PR2920
# Endpoint types (demand d, one-unit capacity b, endpoints) per orientation: PR2909/PR2920.
TYPES = [(36, 24, 12), (44, 28, 24), (45, 30, 8), (46, 29, 24), (47, 30, 24), (48, 30, 12)]
PR2920 = 'b9ea9def949f9d71d59e21294d0e6cfbe0692a73'
PR2920_RESULT = 'research/p104-endpoint-geometric-budget/RESULT.json'
# Lifetime floors: merged #2353/#2383, and the written floors reported in
# discussion 2245 comment 18960667 (fork commit 743640530, not re-proved here);
# 387 is the unproved relay-v2 estimate quoted there.
FLOORS = {208: 'merged #2353/#2383 (PR2920 control)',
          216: 'reported, singular in-frame mixing',
          219: 'reported, invertible in-frame mixing',
          234: 'reported, final-frame-write words',
          387: 'unproved relay-v2 estimate'}
GRID = Q(1, 10 ** 12)


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def check_inputs():
    for record in json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if record['usage'] == 'input':
            data = (ROOT / record['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == record['sha256'], 'pinned input ' + record['path'])


def engine():
    check_inputs()
    spec = importlib.util.spec_from_file_location(
        'ceiling', ROOT / 'research/complex-local-word-ceiling/ceiling.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def curve(types=TYPES):
    """C_min(U): fewest cheap helpers for U unit helpers (sorted marginals b, d-b)."""
    require(sum(n for *_, n in types) == 104, '104 endpoints per orientation')
    marginals = []
    for d, b, n in types:
        require(0 < b < d <= 2 * b, 'two decreasing positive marginals')
        marginals += [b, d - b] * n
    marginals.sort(reverse=True)
    out = [sum(d * n for d, _, n in types)]
    for x in marginals:
        out.append(out[-1] - x)
    require(out[0] == 4656 and out[-1] == 0, 'complete coverage at 208 units')
    return out


def pr2920_curve():
    """Cross-check against PR2920's receipt when its commit is present; else None."""
    shown = subprocess.run(['git', '-C', str(ROOT), 'show', PR2920 + ':' + PR2920_RESULT],
                           capture_output=True, check=False)
    if shown.returncode:
        return None
    result = json.loads(shown.stdout)['geometry']
    return [result[o]['minimum_cheap_by_units'] for o in ('arrival', 'departure')]


def profile(cheap, units):
    return BASE | {1: BASE[1] + 2 * cheap + 9 * units, 7: BASE[7] + cheap}


class Price:
    """Exact-interval affine moment M(C,U) = M00 + C*qc + U*qu at one saving a."""

    def __init__(self, module, a):
        self.module, self.a = module, a
        m00, m10, m01 = (module.relax(profile(c, u), *TEMPLATE, a) for c, u in ((0, 0), (1, 0), (0, 1)))
        self.m00 = m00
        self.qc = (m10[0] - m00[1], m10[1] - m00[0])
        self.qu = (m01[0] - m00[1], m01[1] - m00[0])
        require(self.qc[0] > 0 and self.qu[0] > 0, 'positive helper prices')

    def __call__(self, cheap, units):
        return (self.m00[0] + cheap * self.qc[0] + units * self.qu[0],
                self.m00[1] + cheap * self.qc[1] + units * self.qu[1])

    def direct(self, cheap, units):
        return self.module.relax(profile(cheap, units), *TEMPLATE, self.a)


def candidates(floor, cmin):
    """Minimal-cheap feasible pairs; extra cheap helpers only add positive price."""
    for units in range(MAX_LIFETIMES + 1):
        cheap = max(cmin[min(units, 208)], floor - units, 0)
        if cheap + units <= MAX_LIFETIMES:
            yield cheap, units


def optimum(price, floor, cmin):
    pairs = list(candidates(floor, cmin))
    best = min(pairs, key=lambda p: price(*p)[1])
    hi = price(*best)[1]
    require(all(price(*p)[0] > hi for p in pairs if p != best), 'certified unique optimizer')
    direct = price.direct(*best)
    lo, up = price(*best)
    require(lo <= direct[1] and direct[0] <= up, 'affine enclosure agrees with direct relax')
    return best, direct


def root(module, pair):
    lo, hi = Q(0), Q(1, 100)
    require(module.relax(profile(*pair), *TEMPLATE, hi)[0] > 1, 'root window')
    while hi - lo > GRID:
        mid = Q(int((lo + hi) / 2 / GRID)) * GRID
        if mid <= lo:
            mid = lo + GRID
        value = module.relax(profile(*pair), *TEMPLATE, mid)
        require(value[1] < 1 or value[0] > 1, 'enclosure separates grid point')
        lo, hi = (mid, hi) if value[1] < 1 else (lo, mid)
    return lo, hi


def threshold(price, cmin):
    """Smallest floor whose certified two-type minimum moment exceeds one."""
    passes = lambda floor: price(*optimum(price, floor, cmin)[0])[1] < 1
    rejects = lambda floor: all(price(*p)[0] > 1 for p in candidates(floor, cmin))
    lo, hi = 208, MAX_LIFETIMES
    require(passes(lo) and rejects(hi), 'threshold window')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if passes(mid):
            lo = mid
        else:
            require(rejects(mid), 'decided floor')
            hi = mid
    best, direct = optimum(price, hi, cmin)
    return hi, best, direct


def compute():
    module, cmin = engine(), curve(TYPES)
    source = pr2920_curve()
    if source is not None:
        require(source == [cmin, cmin], 'curve equals PR2920 receipt in both orientations')
    price = Price(module, SELECTED)
    floors = {}
    for floor, label in FLOORS.items():
        (cheap, units), direct = optimum(price, floor, cmin)
        r = root(module, (cheap, units))
        floors[str(floor)] = {
            'source': label, 'cheap': cheap, 'units': units, 'lifetimes': cheap + units,
            'selected_moment': [str(x) for x in direct], 'passes': direct[1] < 1,
            'root_bracket': [str(x) for x in r]}
    reject_floor, (cheap, units), direct = threshold(price, cmin)
    require(floors['208']['cheap'] == 0 and floors['208']['units'] == 208, 'PR2920 optimum reproduced')
    return {'floors': floors,
            'first_rejecting_floor': {'lifetimes': reject_floor, 'cheap': cheap, 'units': units,
                                      'selected_moment': [str(x) for x in direct]},
            'pr2920_curve_checked': source is not None,
            'scope': 'Two-history separate-endpoint ideal-idle relaxation of PR2920 only; '
                     'reported floors imported, not re-proved; no construction or kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.emit:
        print(encoded)
        return
    expected = json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8'))
    expected['pr2920_curve_checked'] = result['pr2920_curve_checked']
    require(json.dumps(expected, indent=2, sort_keys=True) == encoded, 'typed receipt')
    f = result['floors']
    print('PASS_P104_TWO_HISTORY_LIFETIME_FLOOR '
          + ' '.join('L%s=(%d,%d)' % (k, v['cheap'], v['units']) for k, v in f.items())
          + ' first_rejecting_floor=%d' % result['first_rejecting_floor']['lifetimes']
          + ' pr2920_curve_checked=%s no_new_kappa' % result['pr2920_curve_checked'])


if __name__ == '__main__':
    main()
