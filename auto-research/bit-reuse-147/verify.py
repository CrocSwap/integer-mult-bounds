#!/usr/bin/env python3
"""Verify the recycled bit word from the pinned sources (Python stdlib only; a few minutes; do not use -O).

  1. #144 control.  On #144's own 10^-10 grid, the merged #144 row prices to its coarse saving 4617656/10^10,
     stopped saving 4613422943/10^13 and kappa 4609169/10^10 exactly, with the next grid points rejected.
  2. Timetable control.  With no elimination and no recycling, the delayed-read word of this package reproduces every
     histogram of #144's reconstruct() row: delaying reads in the inherited order changes no charge.
  3. The frozen plan is legal, its timetable satisfies every ordering constraint, and the frame ledger runs: every
     scalar gate finds its registers at one common frame key and no register ever retreats.  The row rebuilt from the
     actual ledger moves equals row.json.
  4. Every adjacent frame pair that is not an ordered pair of one inherited certified chain is nested exactly over Q
     and both frames are nondegenerate.  Control: a recipient given a donor whose frame is not inside sigma is
     rejected by the same test.
  5. The literal scalar word on the physical registers.  First on formal variables, over F2 and over Z with the
     exact integer read coefficients: every register must end as its own variable and every target as its start
     variable plus exactly its defining sum.  This is complete and uses no random vectors.  Then with random
     scratch and data, where three tampered words must break the Z identity: a recycled read of the register's
     entrance value, a recycled read taken before its donor's last write, and the inherited inverse order.
  6. #144's assembly on the new row: kappa and its next grid point, at the merged atom exponent 1/1000 and at 1/2000.
Usage: python3 research/bit-reuse-147/verify.py [--all]
  --all also checks exact nesting of every distinct ledger move, including those the pinned audits already certify
  (about seven more minutes).
"""
import json
import random
import sys
import time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
def log(*a): print('[%5.0fs]' % (time.time() - T0), *a, flush=True)

EXPECT = json.loads((HERE / 'expected.json').read_text())


def clean(H): return {str(k): n for k, n in H.items() if n}


def main():
    assert not sys.flags.optimize, 'run without -O'
    import word147
    import price147
    from frames147 import Exact
    from paired_cube_bit import reconstruct
    ROOT = word147.ROOT

    base = reconstruct()
    r0 = price147.price(base, grid=10**10)
    assert (r0['coarse'], r0['stopped'], r0['kappa']) == (Q(4617656, 10**10), Q(4613422943, 10**13), Q(4609169, 10**10)), r0
    log('PASS #144 control: coarse 4617656/10^10, stopped 4613422943/10^13, kappa 4609169/10^10 (next rejected)')

    dr, W, D, S, record, folder = word147.load_schedule()
    outputs = {(c, tuple(T)): n for c, T, n in W['outputs']}
    sel = json.loads((ROOT / record['selection_file']).read_text())
    plain = word147.Word(S, [], sel['retained_readout_order'], [])
    led0 = plain.ledger(); row0 = plain.row(led0, record)
    for key in ('auxiliary_histogram', 'source_data_histogram', 'target_data_histogram', 'selected_rank_histogram',
                'child_histogram'):
        assert clean(row0[key]) == clean(base[key]), key
    assert (row0['R'], row0['W_per_vertex'], row0['rank_per_vertex']) == (base['R'], base['W_per_vertex'], base['rank_per_vertex'])
    assert plain.replay(2, random.Random(1), outputs) and plain.replay(0, random.Random(2), outputs)
    log('PASS timetable control: #144 row reproduced with reads delayed to positions %d..%d of %d; replay holds' % (
        min(plain.p.values()), max(plain.p.values()), plain.N))

    plan = json.loads((HERE / 'plan.json').read_text())
    assert set(plan['retained']) <= set(sel['retained_readout_order']), "level slots are among #144's selected gauges"
    assert {b for b, _ in plan['pairs']} <= set(sel['retained_readout_order'])
    word = word147.Word(S, plan['elim'], plan['retained'], plan['pairs'])
    led = word.ledger(); row = word.row(led, record)
    assert row == json.loads((HERE / 'row.json').read_text()), 'row differs'
    occupants = Counter(led['phys'].values())
    log('PASS ledger: %d eliminated, %d recycled, %d physical roles (longest occupant chain %d); row equals row.json' % (
        len(plan['elim']), len(plan['pairs']), row['R'], max(occupants.values())))

    exact = Exact(S, W, folder)
    fresh = word.new_moves(led)
    kinds = Counter((reg, a[0], b[0]) for reg, a, b in fresh)
    for reg, a, b in fresh:
        assert exact.inside(a, b), ('not nested', reg, a, b)
        assert exact.nondegenerate(a) and exact.nondegenerate(b), ('degenerate', a, b)
    handoffs = {(('n', 0), ('sigma', b)) for b in word.donor_of}
    assert kinds['a', 'n', 'sigma'] + kinds['a', 'ret', 'sigma'] + kinds['a', 'c', 'sigma'] + kinds['a', 'v', 'sigma'] + \
        kinds['a', 'sigma', 'sigma'] + kinds['a', 'out', 'sigma'] <= len(handoffs)
    assert all(reg == 'y' or b[0] == 'sigma' for reg, a, b in fresh), 'only hand-offs and target chains are new'
    rng = random.Random(20261009); rejected = 0; tried = 0
    donors = sorted(word.recipient_of)
    while tried < 200:
        b = rng.choice(sorted(word.donor_of)); d = rng.choice(donors)
        key = [k for k in S.chain_keys(d) if k[0] != 'F'][-1]
        if S.dim(key) > S.f[b]: continue
        tried += 1; rejected += not exact.inside(key, ('sigma', b))
    assert rejected > 0, 'the nesting test never rejects'
    log('PASS exact nesting over Q of all %d new adjacent pairs %s; control rejected %d of %d mismatched hand-offs' % (
        len(fresh), dict(kinds), rejected, tried))
    if '--all' in sys.argv:                                 # optional: every distinct move, inherited ones included
        every = sorted(led['moves'], key=str)
        for reg, a, b in every: assert exact.inside(a, b), ('not nested', reg, a, b)
        log('PASS exact nesting over Q of all %d distinct ledger moves, inherited ones included' % len(every))

    assert word.complete(2, outputs) and word.complete(0, outputs), 'scalar identity on formal variables'
    log('PASS complete scalar identity on all %d formal variables, over F2 and over Z (no random vectors)' % (2 * S.v + row['R']))
    rng = random.Random(20261009)
    okF = all(word.replay(2, rng, outputs) for _ in range(3)); okZ = all(word.replay(0, rng, outputs) for _ in range(2))
    assert okF and okZ, 'scalar identity'
    for tamper in ('stale', 'early', 'vlast'):
        assert not word.replay(0, rng, outputs, tamper), 'tamper accepted: ' + tamper
    log('PASS literal replay on %d physical registers over Z and F2; stale read, premature read and inherited inverse '
        'order all rejected' % row['R'])

    for atom, name in ((None, 'kappa'), (Q(1, 2000), 'kappa_atom_2000')):
        r = price147.price(row, atom)
        assert str(r['kappa']) == EXPECT[name] and str(r['coarse']) == EXPECT['coarse'], (name, str(r['kappa']), str(r['coarse']))
        log('PASS atom %s: kappa %s = %.10e (next %s rejected); coarse %s, stopped %.12e, R %d, W %d, largest child %d' % (
            r['atom'], r['kappa'], float(r['kappa']), r['kappa_next_rejected'], r['coarse'], float(r['stopped']),
            r['R'], r['W_per_vertex'], r['maxchild']))


if __name__ == '__main__':
    main()
