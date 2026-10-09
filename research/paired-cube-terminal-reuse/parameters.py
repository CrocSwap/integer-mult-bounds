#!/usr/bin/env python3
"""Exact supplier and assembly arithmetic for independently replayed local words.

Apache-2.0. huxint, with substantial OpenAI Codex assistance.
Retains icekylinx's shared-core assembly and full finite router (PR144),
eumemic's PR157 words, and the stopped-bit adapter condition. Interval
arithmetic is the independent maintainer implementation in
scripts/audit_community_candidate.py, with cached logarithms.

This module proves arithmetic implications of its input inventories. The
package's verifier must reconstruct those inventories from physical words.
"""

from functools import lru_cache
from fractions import Fraction as Q
from math import exp, fsum, log, prod
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_community_candidate import GRID as ROUNDING, exp_bounds, log_bounds
from certify import require
from paired_cube_network import finite_bridge
from structured_bulk_assembly import js
from paired_cube_assembly import assembly

BAD = Q(1, 10**16)
OLD = Q(384599, 10**10)
SUPPLIER_GRID = 10**12
ATOM_GRID = 10**12
KAPPA_GRID = 10**12
ETA = Q(1, 10**12)
PHASE_STOP = Q(1, 10**12)
PHASE_GAP = Q(1, 10**15)


def counts(row):
    """Check dimensions and rank mass after a physical verifier recounts them."""
    h, v, loss = (row[k] for k in ('h', 'v', 'loss'))
    roles = row.get('physical_R', row['R'])
    m, width = 3*h, 2*v+roles
    hist = {int(r): n for r, n in row['child_histogram'].items() if int(r) and n}
    require(all(isinstance(n, int) and n > 0 and 0 < r < m for r, n in hist.items()),
            'Proper positive child inventory')
    mass = sum(r*n for r, n in hist.items())
    require((m, width, mass, width*m-mass) ==
            (row['m'], row['W_per_vertex'], row['rank_per_vertex'], row['deficit_per_vertex']),
            'Physical dimensions and rank recount')
    require(width*m-mass == 2*v-3*loss > 0, 'Shared-core telescoping deficit')
    return dict(m=m, local_dimension=h, W_per_vertex=width,
                rank_per_vertex=mass, deficit_per_vertex=width*m-mass,
                child_multiplicities=dict(sorted(hist.items())),
                maxchild=max(hist), edge_count=sum(hist.values()), physical_roles=roles)


@lru_cache(maxsize=None)
def logarithms(m, r):
    return log_bounds(Q(m, r))


def interval_moment(profile, saving, *, bit=False):
    """Outward bounds on the full characteristic, including every bad edge."""
    require(0 <= saving < Q(1, 32), 'Saving range')
    m, width = profile['m'], profile['W_per_vertex']
    entries = list(profile['child_multiplicities'].items())
    if bit:
        # This adds the entire fallback to every ideal edge. It never
        # subtracts a hypothetical good edge from the bad-class charge.
        entries.append((1, BAD*32*m*m*profile['edge_count']))
    lower = upper = Q(0)
    for rank, multiplicity in entries:
        require(0 < rank < m and multiplicity > 0, 'Moment entry')
        lo, hi = logarithms(m, rank)
        weight = Q(rank, width*m)*multiplicity
        lower += weight*exp_bounds(saving*lo)[0]
        upper += weight*exp_bounds(saving*hi)[1]
    return Q((lower*ROUNDING).__floor__(), ROUNDING), Q((upper*ROUNDING).__ceil__(), ROUNDING)


def select_supplier(profile, *, bit=False, denominator=SUPPLIER_GRID):
    """Discover a grid point numerically, then certify it and its successor."""
    m, width = profile['m'], profile['W_per_vertex']
    entries = list(profile['child_multiplicities'].items())
    if bit:
        entries.append((1, float(BAD)*32*m*m*profile['edge_count']))
    numerical_terms = [(r*n/(width*m), log(m/r)) for r, n in entries]
    lo, hi = 0., 1/32
    for _ in range(60):
        mid = (lo+hi)/2
        if fsum(weight*exp(mid*ell) for weight, ell in numerical_terms) < 1:
            lo = mid
        else:
            hi = mid
    candidate = max(1, int(lo*denominator))
    for _ in range(10):
        saving = Q(candidate, denominator)
        lower, upper = interval_moment(profile, saving, bit=bit)
        if upper >= 1:
            require(lower >= 1, 'Enclosure straddles one; increase precision')
            candidate -= 1
            continue
        next_lower, next_upper = interval_moment(profile, saving+Q(1, denominator), bit=bit)
        if next_upper < 1:
            candidate += 1
            continue
        require(next_lower >= 1, 'Successor enclosure straddles one; increase precision')
        result = dict(saving=saving, moment_lower=lower, moment_upper=upper,
                      strict_gap=1-upper, next_grid_saving=saving+Q(1, denominator),
                      next_grid_moment_lower=next_lower, grid_denominator=denominator,
                      interval_rounding_denominator=ROUNDING)
        if bit:
            fallback = 32*m*m
            rank_upper = Q(profile['rank_per_vertex'])+BAD*fallback*profile['edge_count']
            require(rank_upper < width*m, 'Contaminated rank moment')
            require(Q(2*m**3, 2**80) < BAD, 'Fixed-prime bad-class allowance')
            result.update(bad_fraction=BAD, fallback_children_per_edge=fallback,
                          rank_mass_upper_per_vertex=rank_upper)
        return result
    raise ValueError('Numerical discovery did not locate the certified grid interval')


def choose_atom(coarse, *, denominator=ATOM_GRID):
    """Choose the first rational grid point strictly above the adapter floor."""
    require(OLD < coarse < 1, 'Coarse saving must improve the ordinary leaf')
    threshold = coarse/(1+coarse-OLD)
    atom = Q((threshold*denominator).__floor__()+1, denominator)
    effective = (1-atom)*coarse+atom*OLD
    require(effective < atom < 1-effective, 'Subordinate adapter and row tolls')
    require(atom-Q(1, denominator) <= threshold < atom, 'Strict atom grid floor')
    return dict(atom_exponent=atom, effective_saving=effective,
                strict_lower_bound=threshold, lower_toll_gap=atom-effective,
                upper_toll_gap=1-effective-atom, ordinary_leaf_saving=OLD,
                grid_denominator=denominator)


def certificate(complex_row, bit_row, source_row):
    require(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    require((source_row['h'], source_row['v']) == (complex_row['h'], complex_row['v']),
            'Scalar source and physical complex dimensions agree')
    require(source_row['R'] >= complex_row['R'], 'Conservative logical scalar role stock')
    cp, bp = counts(complex_row), counts(bit_row)
    cs, bs = select_supplier(cp), select_supplier(bp, bit=True)
    atom = choose_atom(bs['saving'])
    ac, ab = cs['saving'], atom['effective_saving']
    m = cp['m']
    require(m % 2 == 0, 'Retained even-dimensional complex cover')
    half = m//2
    vertices = 2**(m-1+(half-1)**2)*prod(2**(2*i)-1 for i in range(1, half))
    phase = dict(counts=cp, **cs, vertices_per_stage=vertices,
                 N=vertices*complex_row['v'], W=vertices*cp['W_per_vertex'],
                 total_rank=vertices*cp['rank_per_vertex'],
                 deficit=vertices*cp['deficit_per_vertex'], group_order_bits=vertices.bit_length())
    bit = dict(counts=bp, coarse=bs, **atom)
    # The source row retains the uncompressed logical word. Its conservative
    # operation/readout allowance pays the same word with fewer physical slots.
    bridge = finite_bridge(phase, bit, source_row)
    bridge['bit_uniform'].update(coarse_saving=bs['saving'], atom_beta=atom['atom_exponent'],
                                 old_atom_saving=OLD, ordinary_saving=ab)
    a = min(ab, (1-PHASE_STOP)*ac-PHASE_GAP)
    initial = assembly(a, ac, bridge, Q(0), eta=ETA, beta=PHASE_STOP)
    minimum = initial['minimum_margin']
    kappa = Q((minimum.numerator*KAPPA_GRID-1)//minimum.denominator, KAPPA_GRID)
    result = assembly(a, ac, bridge, kappa, eta=ETA, beta=PHASE_STOP)
    require(kappa < minimum <= kappa+Q(1, KAPPA_GRID), 'Strict assembly grid interval')
    # The failing call is alone inside this try. Never catch an assertion
    # supplied by the negative-control test itself.
    try:
        assembly(a, ac, bridge, kappa+Q(1, KAPPA_GRID), eta=ETA, beta=PHASE_STOP)
    except AssertionError:
        pass
    else:
        raise ValueError('Next assembly grid point was accepted')
    require(len(result['strict_constraints']) == 47 and len(result['margins']) == 7,
            'Complete retained assembly')
    return dict(kappa=kappa, complex=phase, bit=bit, finite_bridge=bridge, assembly=result,
                next_grid_kappa=kappa+Q(1, KAPPA_GRID), next_grid_rejected=True,
                scope='Exact arithmetic for independently reconstructed physical inventories, '
                      'retaining the analytic, uniform-recursion and fixed-tape hypotheses.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex', type=Path, required=True)
    parser.add_argument('--bit', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT/'certificates/paired-cube-complex-input.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    result = certificate(*(json.loads(p.read_text()) for p in (args.complex, args.bit, args.source)))
    args.output.write_text(json.dumps(js(result), sort_keys=True, indent=2)+'\n')
    print('PASS arithmetic: kappa=%s (%.12g); both supplier successors and assembly successor rejected'
          % (result['kappa'], float(result['kappa'])))


if __name__ == '__main__':
    main()
