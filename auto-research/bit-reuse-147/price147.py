"""Price a shared-core bit row with the merged #144 arithmetic (scripts/paired_cube_network.py, icekylinx).

Stdlib only.  The functions used are #144's own: exact_moment(), the rare-class contamination of bit_certificate(),
complex_certificate(), finite_bridge() and the 47-constraint assembly.  As in hpst3r's #147, the one relaxed check is
the bit dimension test, which here accepts R <= 28866; every other check of shared_profile() is kept verbatim.  The
coarse saving and kappa are the largest points of a 10^-12 grid that pass, and the next points are rejected.  On
#144's own 10^-10 grid and row this reproduces 4617656/10^10, 4613422943/10^13 and 4609169/10^10 exactly.
"""
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import paired_cube_network as pcn  # noqa: E402

GRID = 10**12


def bit_profile(row):
    require = pcn.require
    h, v, R, ell = (row[k] for k in ('h', 'v', 'R', 'loss'))
    m, W, H = 3 * h, 2 * v + R, Counter()
    selected = {int(r): n for r, n in row['selected_rank_histogram'].items()}
    require(sum(selected.values()) == row['selected_roles'], 'Selected gauge count')
    for r, n in selected.items():
        require(0 < r < h and n > 0, 'Proper local gauges')
        H[3 * r] += n
    require((h, v, ell) == (23, 1771, 506) and 0 < R <= 28866, 'Retained bit local dimensions (R reduced)')
    for name in ('auxiliary_histogram', 'source_data_histogram', 'target_data_histogram', 'copied_center_histogram'):
        for r, n in row[name].items():
            H[int(r)] += 3 * n
    H[2] += 2 * v
    H = pcn.clean(H)
    require(all(0 < r < m and n > 0 for r, n in H.items()), 'Proper shared-core children')
    mass = sum(r * n for r, n in H.items())
    require(H == pcn.clean(row['child_histogram']), 'Saved complete child histogram')
    require((m, W, mass, W * m - mass) == (row['m'], row['W_per_vertex'], row['rank_per_vertex'], row['deficit_per_vertex']),
            'Saved sharing dimensions and rank')
    require(W * m - mass == 2 * v - 3 * ell, 'Shared-core telescoping deficit')
    return dict(m=m, local_dimension=h, W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=W * m - mass,
                child_multiplicities=H, maxchild=max(H), edge_count=sum(H.values()))


def bit_gap(p, coarse):
    """bit_certificate()'s strict moment gap at a coarse saving, or None if either strict inequality fails."""
    try:
        exact = pcn.exact_moment(p, coarse)
    except (AssertionError, ValueError):
        return None
    m, W = p['m'], p['W_per_vertex']; fallback = 32 * m * m
    added = pcn.BAD * Q(fallback * p['edge_count'], W * m) * pcn.exp_upper(coarse * pcn.log_upper(Q(m)))
    rank_upper = Q(p['rank_per_vertex']) + pcn.BAD * fallback * p['edge_count']
    gap = 1 - exact['moment_upper'] - added
    return gap if gap > 0 and rank_upper < W * m else None


def largest(ok, lo, hi):
    assert ok(lo) and not ok(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def price(row, atom=None, grid=GRID):
    """atom None: the merged #144 atom exponent 1/1000.  grid 10^10 is #144's own grid."""
    atom = pcn.ATOM if atom is None else atom
    p = bit_profile(row)
    assert Q(2 * p['m']**3, 2**80) < pcn.BAD
    k = largest(lambda k: bit_gap(p, Q(k, grid)) is not None, 4 * grid // 10**4, 6 * grid // 10**4)
    coarse = Q(k, grid)
    ab = (1 - atom) * coarse + atom * pcn.OLD
    assert ab < atom < 1 - ab, 'Subordinate adapter and row tolls'
    assembly_bit = min(ab, (1 - pcn.PHASE_STOP) * pcn.AC - Q(1, 10**10))
    assert assembly_bit == ab, 'the bit side still binds'
    crow = json.loads((ROOT / 'certificates' / 'paired-cube-complex-input.json').read_text())
    phase = pcn.complex_certificate(crow)
    bridge = pcn.finite_bridge(phase, None, crow)
    assert Q(json.loads((ROOT / 'certificates' / 'copied-centers-network.json').read_text())['bit']['saving']) == pcn.OLD
    def accepts(kk):
        try: pcn.assembly(assembly_bit, pcn.AC, bridge, Q(kk, grid), beta=pcn.PHASE_STOP)
        except (AssertionError, ValueError): return False
        return True
    kap = largest(accepts, 0, int(pcn.AC * grid) + 1)
    res = pcn.assembly(assembly_bit, pcn.AC, bridge, Q(kap, grid), beta=pcn.PHASE_STOP)
    assert len(res['strict_constraints']) == 47 and len(res['margins']) == 7
    assert all(value > 0 for value in res['strict_constraints'].values())
    return dict(R=row['R'], W_per_vertex=p['W_per_vertex'], maxchild=p['maxchild'], atom=atom,
                coarse=coarse, coarse_gap=bit_gap(p, coarse), coarse_next_rejected=Q(k + 1, grid),
                stopped=ab, complex=pcn.AC, kappa=Q(kap, grid), kappa_next_rejected=Q(kap + 1, grid),
                absorption_gap=res['absorption_gap'])


if __name__ == '__main__':
    assert not sys.flags.optimize
    row = json.loads(Path(sys.argv[1]).read_text())
    for atom in (None, Q(1, 2000)):
        r = price(row, atom)
        print('atom %s: R %d W %d coarse %s stopped %.12e kappa %s = %.10e' % (
            r['atom'], r['R'], r['W_per_vertex'], r['coarse'], float(r['stopped']), r['kappa'], float(r['kappa'])))
