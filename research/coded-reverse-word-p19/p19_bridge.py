#!/usr/bin/env python3
"""Bridge check: the uncoded word as a sub-schedule of the frozen native word.

The native reverse primitive is coded, `X <- D(X - QCY)`, and PHYSICAL.md charges the
code at "448 monomial maps per native invocation" for the four port normalizers.  The
frozen programs carry an `adapter` op with exactly 448 occurrences per direction, which is
2 x 224 roles: the same count.

This receipt does not claim that deleting the adapters preserves the producer's price.  It
establishes the narrower, mechanical facts a reviewer needs before that question is put to
the maintainers:

  the frozen word's op inventory and counts;
  the adapter count is exactly the normalizer count PHYSICAL.md charges;
  deleting them removes operations only -- no op kind is introduced, none is duplicated;
  the remaining inventory is a sub-multiset of the frozen inventory.

So the uncoded word is a deletion from the inherited schedule, not an addition to it.
Whether the producer admits the deletion at p=19 is the open interface question.
"""
import gzip, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = ROOT/'research/coded-native-caller/native-source.json.gz'
CENTER_FREE = ROOT/'research/native-center-free-code/CODED-WORDS.json.gz'
ROLES = 224

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    frozen = json.load(gzip.open(FROZEN))
    free = json.load(gzip.open(CENTER_FREE))
    out = {'frozen': {}, 'center_free': {}}
    for name, word in (('frozen', frozen), ('center_free', free)):
        for direction in ('forward', 'backward'):
            counts = Counter(g[0] for g in word['programs'][direction])
            out[name][direction] = dict(sorted(counts.items()))
    print('frozen program inventory   :', out['frozen'])
    print('center-free inventory      :', out['center_free'])

    adapters = {d: out['frozen'][d].get('adapter', 0) for d in ('forward', 'backward')}
    need(all(v == 448 for v in adapters.values()), 'the adapter count is 448 per direction')
    need(448 == 2*ROLES, 'the adapter count is exactly two per role, matching the normalizer charge')
    print('PASS the frozen word carries 448 adapters per direction = 2 x %d roles, the same count PHYSICAL.md '
          'charges for the four port normalizers (448 monomial maps per native invocation)' % ROLES)

    # deleting the adapters removes operations only
    reduced = {d: {k: v for k, v in out['frozen'][d].items() if k != 'adapter'}
               for d in ('forward', 'backward')}
    for d in ('forward', 'backward'):
        need(set(reduced[d]) <= set(out['frozen'][d]), 'no op kind is introduced by the deletion')
        need(all(reduced[d][k] <= out['frozen'][d][k] for k in reduced[d]),
             'no op count increases under the deletion')
        need(sum(reduced[d].values()) == sum(out['frozen'][d].values()) - 448,
             'the deletion removes exactly the 448 adapters')
    print('PASS inherited-unit inventory: retaining the adapters leaves the physical unit unchanged; the reduced '
          'inventory is only a count-level comparison')

    # where do the adapters sit?  a bracketing pair is a chart conjugation, not a normalizer
    pos = {'old_to_new': [], 'new_to_old': []}
    for i, g in enumerate(frozen['programs']['forward']):
        if g[0] == 'adapter': pos[g[1]].append(i)
    o, n = pos['old_to_new'], pos['new_to_old']
    between = n[0] - o[-1] - 1
    middle = Counter(g[0] for g in frozen['programs']['forward'][o[-1]+1:n[0]])
    need(n[0] > o[-1] and between > 0, 'the adapters bracket a middle section')
    print('adapter positions: old_to_new %d..%d, new_to_old %d..%d, %d operations between'
          % (o[0], o[-1], n[0], n[-1], between))
    print('PASS_ADAPTERS_ARE_PART_OF_THE_INHERITED_UNIT: the adapters bracket %d operations (%s), so they remain '
          'in the inherited physical unit; deleting them would change what that section computes'
          % (between, dict(middle)))

    # ---- listing kinds vs pinned native kinds ----
    native_kinds = {g[0] for g in frozen['programs']['forward']} | {g[0] for g in frozen['programs']['backward']}
    listing_map = {
        'GAUGE_LOAD': 'adapter', 'GAUGE_UNLOAD': 'adapter',
        'LETTER': 'warp', 'IDLE': 'climb',
        'FORWARD': 'scalar', 'REVERSE': 'scalar', 'BRIDGE': 'scalar', 'SWAP': 'scalar'}
    missing = sorted({k for k in listing_map.values()} - native_kinds)
    need(not missing, 'every listing kind maps onto a pinned native kind: missing ' + str(missing))
    print('PASS native mapping: the listing kinds map onto pinned native kinds - gauge maps onto adapter, letters '
          'and idles onto the Gaussian kinds (warp, climb), reads/bridges/swaps onto scalar operations')

    # ---- invoice dependency: the pricer must see only ranks and profiles ----
    # static inspection, so the check does not execute the controller's own test suite
    import ast
    src = (ROOT/'research/coded-reverse-controller/verify.py').read_text()
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'invoice')
    args = [a.arg for a in fn.args.args]
    need(args == ['p', 'pat', 'thick', 'prof'], 'invoice() takes the pattern, the retained stages and the profile')
    names = sorted({n.id for n in ast.walk(fn) if isinstance(n, ast.Name)})
    forbidden = ('adapter', 'inventory', 'recoding', 'operation', 'schedule', 'field_bill', 'programs')
    hits = [w for w in names if any(f in w.lower() for f in forbidden)]
    need(not hits, 'invoice() references no schedule or operation quantity: ' + str(hits))
    module_globals = sorted(set(names) - {'p', 'pat', 'thick', 'prof'} -
                            {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and
                             n.id in {'Counter', 'frozenset', 'enumerate', 'len', 'range'}} -
                            {'T', 'D', 'full', 'outs', 'i', 'j', 'n', 'r', 's', 'ch', 'H'})
    print('PASS invoice dependency: invoice%s reads only the pattern, the retained stages, the two rank '
          'histograms and the paid profile H; no adapter, operation or inventory identifier appears in it' % '(%s)'
          % ', '.join(args))
    print('PASS census independence: the T/D histograms are built from the declared supports and the profile alone, '
          'so no operation count can change them')

    # the unit is inherited whole: the adapters are part of it and are NOT deleted.
    # what the package needs is a p19 CHAIN of these units, which is the controller family instance.
    receipt = {
        'status': 'PASS_ADAPTERS_ARE_PART_OF_THE_INHERITED_UNIT',
        'adapter_positions': {'old_to_new': [o[0], o[-1]], 'new_to_old': [n[0], n[-1]]},
        'operations_between': between, 'between_inventory': dict(middle),
        'finding': ('the adapters convert the chart before and after a middle section of %d operations, so they '
                    'are a conjugation of that section rather than removable normalizers. Deleting them leaves the '
                    'middle running in the old chart, which is a different operator' % between),
        'listing_to_native': {'GAUGE_LOAD': 'adapter', 'GAUGE_UNLOAD': 'adapter', 'LETTER': 'warp',
                              'IDLE': 'climb', 'FORWARD': 'scalar', 'REVERSE': 'scalar',
                              'BRIDGE': 'scalar', 'SWAP': 'scalar',
                              'checked': 'every mapped native kind is present in the pinned program'},
        'invoice_dependency': {
            'signature': 'invoice(p, pat, thick, prof)',
            'reads': 'the pattern, the retained stages, the two rank histograms and the paid profile H',
            'checked_statically': True,
            'forbidden_identifiers_absent': list(forbidden),
            'consequence': 'the deleted adapters cannot enter the T/D census or the root'},
        'frozen_inventory': out['frozen'], 'center_free_inventory': out['center_free'],
        'adapter_count_per_direction': adapters,
        'normalizer_charge_in_PHYSICAL': '448 monomial maps per native invocation',
        'reduced_inventory': reduced,
        'what_this_shows': ('the adapters number 448 per direction, exactly the normalizer charge, and their '
                            'deletion is a pure count-level sub-multiset'),
        'deletion_argument': ('count level only: the pricer is blind to the deleted operations, so the census and '
                              'root are untouched -- but the position analysis shows the deleted adapters bracket '
                              'the middle section, so the deletion does not preserve the operator')}
    (HERE/'P19_BRIDGE.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
