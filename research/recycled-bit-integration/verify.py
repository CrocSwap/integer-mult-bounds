#!/usr/bin/env python3
"""Compose the pinned PR146 gauges, PR147/150 word and PR148 stopping parameter.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Finite conditional verification; retained analytic and uniform interfaces are assumptions.
Default: reconstruct, check exact new frame pairs and complete symbolic scalar maps.
--all: additionally check every distinct inherited frame transition over Q.
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
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/bit-reuse-147'))
import word147
import price147
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
    exact = Exact(S, W, folder)
    for reg, a, b in fresh:
        assert exact.inside(a, b) and exact.nondegenerate(a) and exact.nondegenerate(b), (reg, a, b)
    if args.all:
        for reg, a, b in led['moves']:
            assert exact.inside(a, b), (reg, a, b)
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
