#!/usr/bin/env python3
"""Compose the pinned PR146 gauges, PR147/150 word and PR148 stopping parameter.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Finite conditional verification; retained analytic and uniform interfaces are assumptions.
Default: reconstruct, check exact new frame pairs and complete symbolic scalar maps.
--all: additionally check every distinct inherited frame transition over Q.
Both frame-pair loops run on forked workers (VERIFY_JOBS, default the CPU count); each check is unchanged.
The exact null spaces use an integer fraction-free kernel with output identical to PR97 linalg.null_exact
(VERIFY_NULL=reference uses the original Fraction kernel; VERIFY_NULL=audit runs both and asserts equality).
--write: write the deterministic certificate after all checks pass.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
import multiprocessing
import os
from pathlib import Path
from math import gcd
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/bit-reuse-147'))
import word147
import price147
import frames147
from frames147 import Exact
import paired_cube_network as pcn

ATOM = Q(473, 10**6)
KAPPA = Q(472154791, 10**12)
START = time.monotonic()

def log(message):
    print('[%5.0fs] %s' % (time.monotonic() - START, message), flush=True)

def read(path):
    return json.loads(path.read_text())

def sources():
    paths = [HERE / n for n in ('verify.py', 'PROOF.md', 'NOTICE', 'SOURCE.json',
                               'selection146.json', 'plan.json', 'row.json')]
    paths += sorted((ROOT / 'research/bit-reuse-147').glob('*.py'))
    paths += [ROOT / 'research/bit-reuse-147' / n for n in ('plan.json', 'row.json', 'PROOF.md')]
    paths += [ROOT / 'research/gauge-recycling' / n for n in ('README.md', 'verify.py', 'plan.json', 'row.json')]
    paths += [ROOT / 'research/bit-elim-144/plan.json',
              ROOT / 'scripts/paired_cube_network.py', ROOT / 'scripts/paired_cube_bit.py',
              ROOT / 'scripts/structured_bulk_assembly.py', ROOT / 'scripts/three_stage_cover_network.py',
              ROOT / 'certificates/paired-cube-network.json',
              ROOT / 'certificates/paired-cube-bit-input.json',
              ROOT / 'certificates/paired-cube-complex-input.json']
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}

def null_exact_ff(A, k):
    """For an integer matrix: the same list of rows as PR97 linalg.null_exact (Fraction RREF), fraction-free.

    The steps mirror null_exact one for one: reduce each row by the earlier pivot rows, take its first nonzero
    entry as pivot, clear that column in the earlier rows. Each stored row is a nonzero rational multiple of the
    corresponding Fraction row (pivots kept positive), so the pivots and the reduced row space agree; for each free
    column f, x has x_f = lcm of the pivots and x_pc = -b[f] * lcm / b[pc], a positive multiple of the Fraction
    vector, and dividing by the gcd gives the same primitive vector as linalg.primitive.
    """
    R = []; piv = []; pv = []
    for r0 in A:
        r = list(r0)
        for pc, p, b in zip(piv, pv, R):
            c = r[pc]
            if c: r = [p * x - c * y for x, y in zip(r, b)]
        i = next((i for i, x in enumerate(r) if x), None)
        if i is None: continue
        g = gcd(*r)
        if r[i] < 0: g = -g
        if g != 1: r = [x // g for x in r]
        a = r[i]
        for t, b in enumerate(R):
            c = b[i]
            if c:
                b = [a * x - c * y for x, y in zip(b, r)]; g = gcd(*b)
                if g != 1: b = [x // g for x in b]
                R[t] = b; pv[t] = b[piv[t]]
        R.append(r); piv.append(i); pv.append(a)
    pivots = set(piv); out = []
    for f in range(k):
        if f in pivots: continue
        lcm = 1
        for p, b in zip(pv, R):
            if b[f]: lcm = lcm * p // gcd(lcm, p)
        x = [0] * k; x[f] = lcm
        for pc, p, b in zip(piv, pv, R):
            if b[f]: x[pc] = -b[f] * (lcm // p)
        g = gcd(*x)
        out.append([v // g for v in x] if g != 1 else x)
    return out

_ORIGINAL = {}

def install_null_kernel(folder, mode=None):
    """Replace null_exact in the pinned PR97 modules (and prim in frames147) before Exact is built.

    The frozen files are not edited. Non-integer or ragged input falls back to the original functions."""
    mode = mode or os.environ.get('VERIFY_NULL', 'fast')
    assert mode in ('fast', 'reference', 'audit'), mode
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    import linalg
    import check_lifted
    ref_null = _ORIGINAL.setdefault('null_exact', linalg.null_exact)
    ref_prim = _ORIGINAL.setdefault('prim', frames147.prim)
    if mode == 'reference':
        linalg.null_exact = check_lifted.null_exact = ref_null
        frames147.prim = ref_prim
        return mode
    def integral(A, k):
        return all(len(r) == k and all(type(x) is int for x in r) for r in A)
    def null_fast(A, k):
        A = [list(r) for r in A]  # materialise once, so one-shot iterables are not consumed by the type check
        return null_exact_ff(A, k) if integral(A, k) else ref_null(A, k)
    def null_audit(A, k):
        out = ref_null(A, k)
        assert null_fast(A, k) == out, ('null_exact kernel mismatch', A, k)
        return out
    def prim_fast(r):
        r = list(r)
        for x in r:
            if type(x) is not int: return ref_prim(r)
        g = gcd(*r)
        return [x // g for x in r] if g else list(r)
    def prim_audit(r):
        out = ref_prim(r)
        assert prim_fast(r) == out, ('prim mismatch', r)
        return out
    null, prim = (null_fast, prim_fast) if mode == 'fast' else (null_audit, prim_audit)
    linalg.null_exact = check_lifted.null_exact = null
    frames147.prim = prim
    return mode

_EXACT = None
_NONDEG = False

def _failures(chunk):
    E = _EXACT
    return [(reg, a, b) for reg, a, b in chunk
            if not (E.inside(a, b) and (not _NONDEG or (E.nondegenerate(a) and E.nondegenerate(b))))]

def check_moves(exact, moves, nondegenerate=False):
    """The moves (reg, a, b) whose frame a is not inside b (or, with nondegenerate, either frame is degenerate).

    Each check is a pure function of the shared exact frames, exactly as in the serial loop, so the moves are
    split across forked worker processes (VERIFY_JOBS, default the CPU count). Moves are grouped by target key
    so each worker builds each annihilator basis once. Without fork, or with one job, it runs serially.
    """
    global _EXACT, _NONDEG
    _EXACT, _NONDEG = exact, nondegenerate
    moves = sorted(moves, key=lambda m: (str(m[2]), str(m[1]), str(m[0])))
    jobs = int(os.environ.get('VERIFY_JOBS', os.cpu_count() or 1))
    if jobs <= 1 or len(moves) < 2 * jobs or 'fork' not in multiprocessing.get_all_start_methods():
        return _failures(moves)
    size = -(-len(moves) // (4 * jobs))
    chunks = [moves[i:i + size] for i in range(0, len(moves), size)]
    with multiprocessing.get_context('fork').Pool(jobs) as pool:
        return [m for part in pool.map(_failures, chunks) for m in part]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    provenance = read(HERE / 'SOURCE.json')
    assert sha256((HERE / 'selection146.json').read_bytes()).hexdigest() == provenance['selection146_sha256']
    predecessor = read(ROOT / 'certificates/paired-cube-network.json')
    for name, digest in predecessor['source_sha256'].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, ('Changed predecessor source', name)
    _, W, _, S, record, folder = word147.load_schedule()
    base = read(ROOT / 'research/bit-reuse-147/plan.json')
    selection = read(HERE / 'selection146.json')
    old_selection = read(ROOT / record['selection_file'])
    chosen = set(selection['retained_readout_order'])
    assert len(chosen) == len(selection['retained_readout_order']) == 9730
    assert chosen | set(selection['omitted_readout_order']) == set(S.readout)
    assert chosen.isdisjoint(selection['omitted_readout_order'])
    assert set(old_selection['retained_readout_order']) <= chosen
    assert len(chosen - set(old_selection['retained_readout_order'])) == 187
    assert sorted(base['elim']) == sorted(read(ROOT / 'research/bit-elim-144/plan.json')['elim'])
    recipients = {b for b, _ in base['pairs']}
    plan = dict(elim=base['elim'], pairs=base['pairs'],
                retained=sorted(chosen - set(base['elim']) - recipients))
    assert plan == read(HERE / 'plan.json')
    assert len(plan['pairs']) == len(recipients) == len({d for _, d in plan['pairs']}) == 3338
    assert len(plan['elim']) == len(set(plan['elim'])) == 1549
    word = word147.Word(S, plan['elim'], plan['retained'], plan['pairs'])
    led = word.ledger()
    row = word.row(led, record)
    assert row == read(HERE / 'row.json')
    parallel = read(ROOT / 'research/gauge-recycling/plan.json')
    assert plan['elim'] == parallel['elim'] and plan['pairs'] == parallel['pairs']
    assert set(plan['retained']) == set(parallel['retained'])
    assert row == read(ROOT / 'research/gauge-recycling/row.json')
    assert (row['R'], row['W_per_vertex'], row['rank_per_vertex'], row['deficit_per_vertex']) == (23979, 27521, 1896925, 2024)
    old = word147.Word(S, base['elim'], base['retained'], base['pairs'])
    old_led = old.ledger()
    fresh = word.new_moves(led)
    assert set(fresh) == set(old.new_moves(old_led)), 'Composition changed the new-frame obligations'
    log('PASS exact composed plan, chronological ledger and unchanged set of new frame pairs')
    log('null_exact kernel: %s' % install_null_kernel(folder))
    exact = Exact(S, W, folder)
    failed = check_moves(exact, fresh, nondegenerate=True)
    assert not failed, failed[:5]
    if args.all:
        failed = check_moves(exact, led['moves'])
        assert not failed, failed[:5]
    log('PASS exact rational nesting (%d new pairs%s)' % (len(fresh), '; all inherited pairs checked' if args.all else ''))
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
    assert word.complete(2, outputs) and word.complete(0, outputs)
    log('PASS complete F2 and integer scalar maps with independent arbitrary data, targets and dirty registers')
    rng = random.Random(20261009)
    assert word.replay(2, rng, outputs) and word.replay(0, rng, outputs)
    for tamper in ('stale', 'early', 'vlast'):
        assert not word.replay(0, rng, outputs, tamper), tamper
    log('PASS stale-value, premature-read and incorrect-inverse negative controls')
    priced = price147.price(row, ATOM)
    assert priced['kappa'] == KAPPA
    profile = price147.bit_profile(row)
    moment = pcn.exact_moment(profile, priced['coarse'])
    m, w = profile['m'], profile['W_per_vertex']
    added = pcn.BAD * Q(32*m*m*profile['edge_count'], w*m) * pcn.exp_upper(priced['coarse']*pcn.log_upper(Q(m)))
    assert moment['moment_upper'] + added < 1
    # A separate high-precision evaluation checks the direction and scale of the
    # certified bound. Only the rational enclosure above is used as the proof.
    with localcontext() as ctx:
        ctx.prec = 70
        a = Decimal(priced['coarse'].numerator)/Decimal(priced['coarse'].denominator)
        raw = sum(Decimal(n)/Decimal(w) * (Decimal(r)/Decimal(m)) ** (1-a)
                  for r, n in profile['child_multiplicities'].items())
        upper = Decimal(moment['moment_upper'].numerator)/Decimal(moment['moment_upper'].denominator)
        assert raw <= upper < 1
    crow = read(ROOT / 'certificates/paired-cube-complex-input.json')
    phase = pcn.complex_certificate(crow)
    bridge = pcn.finite_bridge(phase, None, crow)
    bridge['bit_uniform'].update(coarse_saving=priced['coarse'], atom_beta=ATOM, ordinary_saving=priced['stopped'])
    result = pcn.assembly(priced['stopped'], pcn.AC, bridge, KAPPA, beta=pcn.PHASE_STOP)
    assert len(result['strict_constraints']) == 47 and len(result['margins']) == 7
    hashes = sources()
    cert = pcn.js(dict(status='Conditional composed bit-register witness', kappa=KAPPA,
        predecessor='d1d6c070f5a8c684727ee7ec35d930f9ebfa9758', pricing=priced,
        bit_profile=profile, bit_moment=moment, added_bad_moment_upper=added,
        complex=phase, finite_bridge=bridge, assembly=result, source_sha256=hashes,
        finite_checks=dict(new_exact_frame_pairs=len(fresh), scalar_domains=['F2', 'Z'],
                          scalar_formal_inputs=row['W_per_vertex'], corruption_controls=['stale','early','vlast']),
        scope='Exact finite scalar identities, rational new-frame nesting, complete paid profile and conditional assembly. '
              'Retained analytic, fixed-tape, uniform-recursion, prime and ordinary-leaf interfaces remain assumptions. '
              'No global optimum of the combined schedule is claimed.'))
    dest = HERE / 'certificate.json'
    if args.write:
        dest.write_text(json.dumps(cert, indent=2, sort_keys=True)+'\n')
    else:
        assert read(dest) == cert, 'Certificate differs; do not refresh without reviewing the change'
    log('PASS kappa=%s = %.12g; full fallback, both suppliers and 47 constraints' % (KAPPA, float(KAPPA)))

if __name__ == '__main__':
    main()
