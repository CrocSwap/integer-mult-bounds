"""Price a #144 bit row (paired-cube shared-core bit profile) with #144's own functions (stdlib only).

Uses scripts/paired_cube_network.py (icekylinx, PR144) unchanged: shared-profile arithmetic, exact interval moment
exact_moment(), the rare-class contamination of bit_certificate(), the complex certificate, finite_bridge() and the
47-constraint assembly.  Differences, all explicit: (1) the bit profile check accepts R != 28866 (every other check
of shared_profile is kept verbatim); (2) COARSE is the LARGEST point of #144's 10^-10 grid passing bit_certificate's
two strict inequalities, with the next grid point rejected; (3) kappa is the LARGEST point of #144's 10^-10 grid
accepted by the assembly, with the next point rejected.  With #144's own row this reproduces COARSE 4617656/10^10 and
kappa 4609169/10^10 exactly (gate).
Prepared by William Porter with Anthropic Claude assistance.  Apache-2.0."""
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import paired_cube_network as pcn  # noqa: E402

GRID = 10**10


def bit_profile(row):
    """pcn.shared_profile(row, False) with the dimension check relaxed to R > 0 (all other checks verbatim)."""
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


def bit_ok(p, coarse):
    """bit_certificate()'s two strict inequalities at a given coarse saving (verbatim arithmetic)."""
    try:
        exact = pcn.exact_moment(p, coarse)
    except (SystemExit, AssertionError, ValueError):        # certify.require raises ValueError
        return False
    m, W = p['m'], p['W_per_vertex']; fallback = 32 * m * m
    added = pcn.BAD * Q(fallback * p['edge_count'], W * m) * pcn.exp_upper(coarse * pcn.log_upper(Q(m)))
    rank_upper = Q(p['rank_per_vertex']) + pcn.BAD * fallback * p['edge_count']
    return 1 - exact['moment_upper'] - added > 0 and rank_upper < W * m


def largest(ok, lo, hi):
    assert ok(lo) and not ok(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def price(row):
    p = bit_profile(row)
    k = largest(lambda k: bit_ok(p, Q(k, GRID)), int(Q(4, 10**4) * GRID), int(Q(6, 10**4) * GRID))
    coarse = Q(k, GRID)
    ab = (1 - pcn.ATOM) * coarse + pcn.ATOM * pcn.OLD
    assert pcn.ATOM > ab and pcn.ATOM < 1 - ab
    assembly_bit = min(ab, (1 - pcn.PHASE_STOP) * pcn.AC - Q(1, 10**10))
    crow = json.loads((ROOT / 'certificates' / 'paired-cube-complex-input.json').read_text())
    phase = pcn.complex_certificate(crow)
    bridge = pcn.finite_bridge(phase, None, crow)
    assert Q(json.loads((ROOT / 'certificates' / 'copied-centers-network.json').read_text())['bit']['saving']) == pcn.OLD
    def accepts(kk):
        try: pcn.assembly(assembly_bit, pcn.AC, bridge, Q(kk, GRID), beta=pcn.PHASE_STOP)
        except (AssertionError, ValueError): return False
        return True
    kap = largest(accepts, 0, int(pcn.AC * GRID) + 1)
    res = pcn.assembly(assembly_bit, pcn.AC, bridge, Q(kap, GRID), beta=pcn.PHASE_STOP)
    assert len(res['strict_constraints']) == 47 and len(res['margins']) == 7
    return dict(R=row['R'], W_per_vertex=p['W_per_vertex'], coarse=coarse, coarse_next_rejected=Q(k + 1, GRID),
                stopped=ab, assembly_bit=assembly_bit, complex=pcn.AC, kappa=Q(kap, GRID),
                kappa_next_rejected=Q(kap + 1, GRID), maxchild=p['maxchild'])


if __name__ == '__main__':
    assert not sys.flags.optimize
    if len(sys.argv) > 1:
        row = json.loads(Path(sys.argv[1]).read_text())
    else:
        from paired_cube_bit import reconstruct
        row = reconstruct()
    r = price(row)
    print('R %d W %d coarse %s stopped %s (%.13e) assembly bit %.13e kappa %s = %.10e (next %s rejected)' % (
        r['R'], r['W_per_vertex'], r['coarse'], r['stopped'], float(r['stopped']), float(r['assembly_bit']),
        r['kappa'], float(r['kappa']), r['kappa_next_rejected']))
