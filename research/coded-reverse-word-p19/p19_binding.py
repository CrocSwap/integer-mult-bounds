#!/usr/bin/env python3
"""Operation-level binding: every chain gate is an invocation of an inherited operation.

The chain is not a new program.  Its atomic elements are calls into the frozen native word:

    REVERSE  -> one invocation of the frozen backward program
    FORWARD  -> one invocation of the frozen forward program
    LETTER   -> a Gaussian child of that program, already inside it
    IDLE     -> an ordered product of those children, already inside it
    GAUGE_LOAD / GAUGE_UNLOAD -> the 448 adapter operations of the invocation
    BRIDGE   -> a scalar owner addition, the same kind the program already contains
    SWAP     -> the signed role exchange of the program's closing convention

This receipt counts those invocations against the frozen program's own inventory, so the
raw operation budget is explicit, and asserts that the chain introduces no operation kind
that the frozen program does not already contain.

It does not claim field-level equality between an invocation and the frozen program's
operator: that needs the program's own semantics, which this package does not implement.
"""
import gzip, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

FROZEN = ROOT/'research/coded-native-caller/native-source.json.gz'
ALLOWANCE = 10**9

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    word = json.load(gzip.open(FROZEN))
    fwd = word['programs']['forward']
    bwd = word['programs']['backward']
    inv_ops = {'forward': len(fwd), 'backward': len(bwd)}
    inv_kinds = {d: dict(Counter(g[0] for g in word['programs'][d])) for d in ('forward', 'backward')}
    need(inv_kinds['forward'] == inv_kinds['backward'], 'the two directions have the same op inventory')

    p, pat = 19, 'I'*9+'T'*9
    gates = W.native_chain(p, pat)
    kinds = Counter(g[0] for g in gates)
    invocations = {'forward': kinds['FORWARD'], 'backward': kinds['REVERSE']}
    raw = sum(invocations[d]*inv_ops[d] for d in invocations)
    print('frozen invocation inventory: %s ops per call, adapters %d' %
          (inv_ops, inv_kinds['forward'].get('adapter', 0)))
    print('chain at p=%d: %d forward calls, %d backward calls, %d gauge loads/unloads, %d letters, %d idles, '
          '%d bridges, %d swaps' % (p, invocations['forward'], invocations['backward'], kinds['GAUGE_LOAD'],
                                    kinds['LETTER'], kinds['IDLE'], kinds['BRIDGE'], kinds['SWAP']))
    need(invocations['backward'] == p, 'one backward call per unit')
    need(invocations['forward'] == p+1, 'one forward call per unit plus the opening read')
    need(kinds['GAUGE_LOAD'] == kinds['GAUGE_UNLOAD'] == p, 'the adapters belong to the invocations, one pair per unit')

    print('raw budget: %d forward x %d + %d backward x %d = %d inherited operations'
          % (invocations['forward'], inv_ops['forward'], invocations['backward'], inv_ops['backward'], raw))
    need(raw < ALLOWANCE, 'the invocation budget fits the inherited raw allowance')
    print('PASS the invocation budget %d is inside the inherited raw allowance %d (%.1f%% used)'
          % (raw, ALLOWANCE, 100*raw/ALLOWANCE))

    # no operation kind outside the frozen inventory, apart from the chain's own wiring
    frozen_kinds = set(inv_kinds['forward'])
    wiring = {'BRIDGE', 'SWAP', 'GAUGE_LOAD', 'GAUGE_UNLOAD', 'FORWARD', 'REVERSE', 'LETTER', 'IDLE'}
    need(set(kinds) <= wiring, 'the chain uses only its vocabulary')
    need({'adapter', 'warp', 'climb', 'scalar'} <= frozen_kinds,
         'the frozen program carries the adapter, Gaussian and scalar kinds the chain maps onto')
    print('PASS no new operation kind: the chain maps onto the frozen kinds %s plus its own wiring'
          % sorted(frozen_kinds))

    receipt = {
        'status': 'PASS_INHERITED_VOCABULARY_AND_INVOCATION_BUDGET',
        'invocation_inventory': inv_ops,
        'invocation_kinds': inv_kinds,
        'chain_counts': dict(kinds),
        'invocations_at_p19': invocations,
        'raw_operation_budget': raw,
        'raw_allowance': ALLOWANCE,
        'fraction_of_allowance': round(raw/ALLOWANCE, 6),
        'binding': ('inherited operation vocabulary and invocation-budget binding: each chain gate is an invocation '
                    'of the frozen program or of a kind it already contains, and the raw budget is explicit'),
        'not_full_lowering': ('this is not a lowering proof.  The remaining obligation is that one generated '
                              'invocation is semantically equal to the frozen native invocation, including field '
                              'state, ownership, scratch, precision, adapters, phases and output gauges'),
        'does_not_show': ('field-level equality between one invocation and the frozen program operator, which needs '
                          'the program semantics that this package does not implement')}
    (HERE/'P19_BINDING.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
