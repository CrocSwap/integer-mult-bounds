#!/usr/bin/env python3
"""Exact parameter refinement of the pinned PR #63 conditional witness.

Prepared with OpenAI Codex assistance. Apache-2.0; inherited notices apply.
Construction: Dominik Scholz (#63), Chafik Boukhalfa (#60), Avi Eisenberg
(#62), eumemic (#57), and the community dependency chain. The parameter-only
approach follows Alejandro Zarzuelo Urdiales (#61). No full theorem claim.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRID = 10**18
ROUND = 10**50
ORDER = 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def floor(x):
    return x.numerator // x.denominator


def ceil(x):
    return -((-x.numerator) // x.denominator)


def exp_bounds(lo, hi):
    """Degree-eight Taylor bounds; omitted-term ratios are at most hi/10."""
    require(0 <= lo <= hi < 1, 'Exponential enclosure domain')
    lower = upper = Q(1)
    lt = ut = Q(1)
    for j in range(1, ORDER + 1):
        lt *= lo / j
        ut *= hi / j
        lower += lt
        upper += ut
    tail = (ut * hi / (ORDER + 1)) / (1 - hi / (ORDER + 2))
    return lower, upper + tail


def moment(arithmetic, m, width, rows, saving):
    require(0 < saving < 1, 'Saving domain')
    lower = upper = Q(0)
    terms = {}
    for t, count in sorted(rows.items()):
        require(0 < t < m and count > 0, 'Invalid child')
        log_lo, log_hi = arithmetic.logs(Q(m, t))
        lo, hi = exp_bounds(saving * log_lo, saving * log_hi)
        weight = Q(t * count, m * width)
        lo = Q(floor(weight * lo * ROUND), ROUND)
        hi = Q(ceil(weight * hi * ROUND), ROUND)
        lower += lo
        upper += hi
        terms[t] = dict(lower=lo, upper=hi)
    return dict(lower=lower, upper=upper, strict_gap=1-upper, terms=terms)


def generate():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                'Pinned source changed: ' + name)
    sys.path.insert(0, str(ROOT / 'scripts/experiments'))
    import binary_frame_math as arithmetic
    path = ROOT / 'references/frame-compiler/pr48/research/copied-fixed/balanced_assembly.py'
    spec = importlib.util.spec_from_file_location('refinement_balanced', path)
    balanced = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(balanced)
    old = json.loads((ROOT / 'research/rank-pair/screen-certificate.json').read_text())
    p = old['bit']
    m, width = p['m'], p['W']
    rows = {int(t): count for t, count in p['child_multiplicities'].items()}
    require(sum(t * n for t, n in rows.items()) == m * width - 1846900,
            'Full paid rank identity changed')
    require(m == 575 and width == 137151806 and max(rows) == 529,
            'Physical dimensions changed')
    lo = floor(Q(old['bit_saving']) * GRID)
    hi = ceil(Q(old['next_bit_saving']) * GRID)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if moment(arithmetic, m, width, rows, Q(mid, GRID))['strict_gap'] > 0:
            lo = mid
        else:
            hi = mid
    saving = Q(lo, GRID)
    accepted = moment(arithmetic, m, width, rows, saving)
    rejected = moment(arithmetic, m, width, rows, Q(hi, GRID))
    require(accepted['upper'] < 1 < rejected['lower'],
            'Adjacent bit grid values not separated by exact bounds')
    backoff = Q(1, GRID)
    bridge = old['finite_bridge']
    trial = balanced.assembly(bridge, saving, Q(old['kappa']), h=backoff)
    kappa = Q(ceil(trial['minimum_margin'] * GRID) - 1, GRID)
    assembled = balanced.assembly(bridge, saving, kappa, h=backoff)
    require(len(assembled['constraints']) == 47 and len(assembled['margins']) == 7,
            'Incomplete assembly')
    try:
        balanced.assembly(bridge, saving, kappa + Q(1, GRID), h=backoff)
    except balanced.InvalidAssembly:
        pass
    else:
        raise ValueError('Adjacent kappa grid value unexpectedly passed')
    require(kappa > Q(old['kappa']), 'No improvement over pinned PR63')
    result = dict(
        status='Exact conditional parameter refinement; inherited construction and hypotheses',
        kappa=kappa, bit_saving=saving, h=backoff,
        grid_denominator=GRID, exponential_order=ORDER, rounding_denominator=ROUND,
        bit=dict(m=m, W=width, child_multiplicities=rows, accepted=accepted,
                 next_saving=Q(hi, GRID), rejected=rejected),
        assembly=assembled, eventual_bounds=balanced.cutoffs(bridge, assembled),
        comparison=dict(pr63_kappa=Q(old['kappa']), absolute_gain=kappa-Q(old['kappa']),
                        relative_gain=kappa/Q(old['kappa'])-1),
        source=manifest,
        scope='Parameter-only refinement of PR63. No new circuit, unconditional '
              'multiplication theorem, global optimality or practical speedup is claimed. '
              'The analytic, all-size compiler, fixed-alphabet tape, routing, prime '
              'selection, precision and recovery obligations remain inherited.')
    return arithmetic.js(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    result = generate()
    path = HERE / 'certificate.json'
    if args.record:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(result == json.loads(path.read_text()), 'Certificate mismatch')
    print('PASS kappa=' + result['kappa'] + '; bit=' + result['bit_saving'])
    print('47 strict inequalities; seven margins; both adjacent grid values rejected')
    print('Absolute gain over pinned PR63: ' + result['comparison']['absolute_gain'])


if __name__ == '__main__':
    main()
