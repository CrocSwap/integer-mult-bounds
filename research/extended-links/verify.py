#!/usr/bin/env python3
"""Verify the extended carrier matching on #161's complex word (Python stdlib only; about one minute; no -O).

  1. Control.  cxlinks.compile_closure() with #161's own frozen arcs and the repository's operation order returns
     #161's certified complex record exactly, and #161's frozen physical record prices to #161's complex saving
     5885669/10^10 and kappa 5878747/10^10 with the functions used below.
  2. The frozen arcs data/arcs.json contain every arc of #161.  compile_closure() accepts them (acyclic, order a
     linear extension, every value span inside its full backward-intersection frame), the repository's gauge
     selection runs unchanged, and the repository's independent checker scripts/paired_cube/verify.py passes on the
     resulting word: signed scalar identity, K, full backward intersections, physical replay of every frame
     movement, gauges and target chains.
  3. The repository's physical-layer checker scripts/paired_cube_physical.py passes on data/frames.json and
     data/pairs.json: value spans, nested spliced role chains, pair chronology, target chains in read order, the
     telescoping deficit and the exact aliased dirty-scratch replay with its three rejected controls.  Its result
     equals data/physical.json.
  4. #161's assembly (scripts/paired_cube_network.py: exact_moment, finite_bridge, the 47-constraint assembly) on
     the new physical record, with #161's bit supplier, phase stop and atom exponent unchanged: the complex saving
     and kappa are the largest points of the 10^-10 grid that pass, and the next points are rejected.
#161 is not on main: its files are rebuilt from the pinned archive baseline-pr161.tar.gz (baseline.py).
Usage: python3 research/extended-links/verify.py
"""
import json
import sys
import time
from collections import Counter
from fractions import Fraction as Q
from math import prod
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
GRID = 10**10


def log(*a): print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


def complex_profile(pcn, row, phys, pinned):
    """pcn.shared_profile(row, True) and pcn.physical_profile(phys, row), line for line, with one change: the role
    count is not pinned to #161's 16011; it must equal c + q - matched and not exceed 16011 (pinned: exactly it)."""
    require = pcn.require
    h, v, R, ell = (row[k] for k in ('h', 'v', 'R', 'loss'))
    m, W, H = 3 * h, 2 * v + R, Counter()
    selected = {int(r): n for r, n in row['selected_rank_histogram'].items()}
    require(sum(selected.values()) == row['selected_roles'], 'Selected gauge count')
    for r, n in selected.items():
        require(0 < r < h and n > 0, 'Proper local gauges')
        H[3 * r] += n
    require((h, v, ell) == (22, 1320, 440) and (R == 16011 if pinned else 0 < R <= 16011), 'Paired-cube local dimensions')
    require(R == row['c'] + row['q'] - row['matched'], 'Compatible carrier roles')
    require(selected == {18: 2970}, 'Selected rank18 gauges')
    for r, n in enumerate(row['remaining_internal_histogram']): H[r] += 3 * n
    for name in ('source_data_histogram', 'target_data_histogram'):
        for r, n in row[name].items(): H[int(r)] += 3 * n
    H[2] += 2 * v
    H = pcn.clean(H)
    require(all(0 < r < m and n > 0 for r, n in H.items()), 'Proper shared-core children')
    mass = sum(r * n for r, n in H.items())
    require(H == pcn.clean(row['child_histogram']), 'Saved complete child histogram')
    require((m, W, mass, W * m - mass) == (row['m'], row['W_per_vertex'], row['rank_per_vertex'], row['deficit_per_vertex']),
            'Saved sharing dimensions and rank')
    require(W * m - mass == 2 * v - 3 * ell, 'Shared-core telescoping deficit')
    require((phys['h'], phys['v'], phys['R'], phys['loss']) == (h, v, R, ell), 'Physical word dimensions')
    require(phys['physical_R'] == R - phys['pairs'] and phys['W_per_vertex'] == 2 * v + phys['physical_R'], 'Physical stock')
    W, H = phys['W_per_vertex'], Counter()
    for name in ('local_histogram', 'source_data_histogram', 'target_data_histogram'):
        for r, n in phys[name].items(): H[int(r)] += 3 * n
    for d, n in phys['physical_gauge_histogram'].items(): H[3 * int(d)] += n
    H[2] += 2 * v
    H = pcn.clean(H)
    require(H == pcn.clean(phys['child_histogram']), 'Saved physical child histogram')
    require(all(0 < r < m and n > 0 for r, n in H.items()), 'Proper shared-core children')
    mass = sum(r * n for r, n in H.items())
    require((m, mass, W * m - mass) == (phys['m'], phys['rank_per_vertex'], phys['deficit_per_vertex']), 'Saved physical rank')
    require(W * m - mass == 2 * v - 3 * ell, 'Shared-core telescoping deficit')
    return dict(m=m, local_dimension=h, W_per_vertex=W, rank_per_vertex=mass, deficit_per_vertex=W * m - mass,
                child_multiplicities=H, maxchild=max(H), edge_count=sum(H.values()), physical_roles=phys['physical_R'],
                reuse_pairs=phys['pairs'], late_reads=phys['late_pairs'], moved_operation_frames=phys['changed_operation_frames'])


def largest(ok, lo, hi):
    assert ok(lo) and not ok(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if ok(mid) else (lo, mid)
    return lo


def price(pcn, row, phys, pinned):
    """Largest complex saving and kappa on the 10^-10 grid, with #161's bit supplier and constants unchanged."""
    p = complex_profile(pcn, row, phys, pinned)
    def moment(k):
        try: return pcn.exact_moment(p, Q(k, GRID))
        except (AssertionError, ValueError): return None
    k = largest(lambda k: moment(k) is not None, 5 * 10**6, 7 * 10**6)
    AC = Q(k, GRID); exact = moment(k)
    m = p['m']; n = m // 2
    vertices = 2**(m - 1 + (n - 1)**2) * prod(2**(2 * i) - 1 for i in range(1, n))     # as pcn.complex_certificate
    phase = dict(counts=p, **exact, vertices_per_stage=vertices, N=vertices * row['v'], W=vertices * p['W_per_vertex'],
                 total_rank=vertices * p['rank_per_vertex'], deficit=vertices * p['deficit_per_vertex'],
                 group_order_bits=vertices.bit_length())
    bridge = pcn.finite_bridge(phase, None, row)
    bit = min(pcn.AB, (1 - pcn.PHASE_STOP) * AC - Q(1, 10**10))
    def accepts(kk):
        try: pcn.assembly(bit, AC, bridge, Q(kk, GRID), beta=pcn.PHASE_STOP)
        except (AssertionError, ValueError): return False
        return True
    kap = largest(accepts, 0, k + 1)
    res = pcn.assembly(bit, AC, bridge, Q(kap, GRID), beta=pcn.PHASE_STOP)
    assert len(res['strict_constraints']) == 47 and len(res['margins']) == 7
    assert all(value > 0 for value in res['strict_constraints'].values())
    return dict(complex=AC, complex_gap=exact['strict_gap'], kappa=Q(kap, GRID), binding='complex' if bit < pcn.AB else 'bit',
                bit=pcn.AB, W=p['W_per_vertex'], maxchild=p['maxchild'], absorption_gap=res['absorption_gap'],
                minimum_margin=res['minimum_margin'], row_degree_gap=bridge['rows']['degree_gap'])


def main():
    import cxlinks
    ROOT = cxlinks.ROOT
    import paired_cube_network as pcn
    import paired_cube_physical as physical
    expected = json.loads((HERE / 'expected.json').read_text())

    g = cxlinks.graph()
    frozen = json.loads((ROOT / 'references/paired-cube/selected-module/matching-arcs.json').read_text())
    certificate = json.loads((ROOT / 'certificates/paired-cube-complex-input.json').read_text())
    _, _, record0, _ = cxlinks.word(g, frozen, repository_order=True)
    assert record0 == certificate, "compile_closure differs from #161's certified record on #161's arcs"
    phys0 = json.loads((ROOT / 'certificates/paired-cube-physical-input.json').read_text())
    r0 = price(pcn, certificate, phys0, pinned=True)
    assert (r0['complex'], r0['kappa']) == (pcn.AC, pcn.KAPPA) == (Q(5885669, GRID), Q(5878747, GRID)), r0
    log("PASS control: #161's arcs give #161's certified record exactly; its physical record prices to "
        'complex 5885669/10^10 and kappa 5878747/10^10 (next points rejected)')

    arcs = cxlinks.load('arcs.json')
    assert {tuple(a) for a in frozen} <= {tuple(a) for a in arcs}, "every arc of #161 is kept"
    baseline, witness, record, word = cxlinks.word(g, arcs)
    checks = cxlinks.verify(g, baseline, witness, word, record)
    assert all(v is True for k, v in checks.items() if k not in ('signed_scalar_pairs_checked', 'selected_roles'))
    log('PASS extended word: %d arcs (%d new), R %d; repository verify() passes (%d signed scalar pairs, %d gauges)' % (
        record['matched'], record['matched'] - len(frozen), record['R'], checks['signed_scalar_pairs_checked'], checks['selected_roles']))

    result = physical.physical(g, witness, word, record, cxlinks.load('frames.json')['frames'], cxlinks.load('pairs.json')['pairs'])
    result = json.loads(json.dumps(result))
    assert result == cxlinks.load('physical.json'), 'physical record differs from data/physical.json'
    log('PASS physical layer: repository checker passes; %d moved frames, %d pairs (%d late), W %d, deficit %d, '
        'replay restored with controls %s rejected' % (result['changed_operation_frames'], result['pairs'], result['late_pairs'],
        result['W_per_vertex'], result['deficit_per_vertex'], ', '.join(result['scalar_replay']['rejected_controls'])))

    r = price(pcn, record, result, pinned=False)
    got = dict(complex=str(r['complex']), kappa=str(r['kappa']), binding=r['binding'])
    assert got == expected, (got, expected)
    log('PASS complex saving %s = %.7e (next rejected, gap %.3e); bit supplier unchanged at %.7e' % (
        r['complex'], float(r['complex']), float(r['complex_gap']), float(r['bit'])))
    log('PASS kappa %s = %.7e (next %s rejected); %s side binds; 47 constraints, 7 margins; largest child %d' % (
        r['kappa'], float(r['kappa']), r['kappa'] + Q(1, GRID), r['binding'], r['maxchild']))
    log('gain over #161: complex %+.3f%%, kappa %+.3f%%' % (100 * (float(r['complex'] / r0['complex']) - 1),
                                                            100 * (float(r['kappa'] / r0['kappa']) - 1)))


if __name__ == '__main__':
    main()
