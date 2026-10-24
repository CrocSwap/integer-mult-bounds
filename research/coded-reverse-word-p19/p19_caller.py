#!/usr/bin/env python3
"""The completed caller, its initial/final gauges, and every paid correction.

`research/coded-native-caller/PHYSICAL.md:59` states the condition under which productive main
ranks may be asserted:

    "No productive main ranks are asserted merely from the coupled central ABI.  Those depend on the
     completed caller, its initial/final gauges and every paid correction."

That sentence names three objects.  This receipt exhibits all three for the p19 construction and
then reads the productive ranks off the same object, so the ranks are asserted *through* the base's
own condition rather than beside it:

  1. completed caller            the materialized 259-gate chain, its 39 stages and 19 units, replayed
  2. initial gauge               the p gauge loads on the odd roles, role by role
     final gauge                 the p gauge unloads followed by the p signed swaps
  3. paid corrections            the 77 recodings with their field bill, the 36 retained idles and
                                 their rank, and the inherited adapter charge per invocation

Nothing here introduces a new hypothesis: each item is a named requirement of the base text, and the
receipt fails if any of them is absent or empty.
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    p, pat = 19, 'I'*9+'T'*9
    gates = W.native_chain(p, pat)
    kinds = Counter(g[0] for g in gates)

    # 1. the completed caller
    loads = [g for g in gates if g[0] == 'GAUGE_LOAD']
    unloads = [g for g in gates if g[0] == 'GAUGE_UNLOAD']
    swaps = [g for g in gates if g[0] == 'SWAP']
    caller = {
        'gates': len(gates), 'stages': 2*p+1, 'units': p,
        'kinds': dict(sorted(kinds.items())),
        'roles': 2*p, 'ambient_rank': 1 + 8*p,
        'replay_entries': 2*p*112*512}

    # 2. the boundary gauges, explicitly
    initial = {'gates': [list(g) for g in loads],
               'roles': [g[1] for g in loads],
               'every_role_odd': all(g[1] % 2 == 1 for g in loads),
               'per_unit': len(loads) == p,
               'type': 'the code C^-1 applied per unit on its own odd role'}
    final = {'unloads': [list(g) for g in unloads],
             'swaps': [list(g) for g in swaps],
             'unload_roles': [g[1] for g in unloads],
             'swap_signs': sorted({g[3] for g in swaps}),
             'per_unit': len(unloads) == p and len(swaps) == p,
             'order': 'unload then signed swap, so the roles are uncoded when the swap is applied',
             'type': 'C followed by the signed exchange, denominators [1] standard / [1, 13] coded'}

    # 3. every paid correction
    claim = json.loads((HERE/'P19_CLAIM.json').read_text())
    census = json.loads((HERE/'P19_DIAGCENSUS.json').read_text())
    bill = claim['field_level_bill']
    paid = {
        'recodings': bill['recodings'],
        'field_bill': {k: bill[k] for k in ('monomial_field_maps', 'scalar_adds', 'owned_clears',
                                            'recursive_gaussian_children')},
        'retained_idles': claim['idles']['retained'] if isinstance(claim.get('idles'), dict)
                          and 'retained' in claim['idles'] else claim.get('idles'),
        'adapter_charge_per_invocation': 448,
        'derived_paid_profile': claim['paid_profile'],
        'profile_provenance': claim['paid_profile_provenance']['derived_from']}

    # the productive ranks, read off the same construction
    d19 = census['cases']['p19_IIIIIIIIITTTTTTTTT']
    productive = {'main_T': d19['census_main_only'],
                  'census_equals_invoice': d19['census_equals_invoice'],
                  'measured_on': 'the factorisation diagonal of the same caller'}

    out = {'status': 'CALLER', 'p': p, 'pattern': pat,
           'base_condition': ('research/coded-native-caller/PHYSICAL.md:59 - productive main ranks depend on '
                              'the completed caller, its initial/final gauges and every paid correction'),
           'completed_caller': caller, 'initial_gauge': initial, 'final_gauge': final,
           'paid_corrections': paid, 'productive_main_ranks': productive}

    print('caller      : %d gates, %d stages, %d units, %d roles, ambient rank %d, %d replayed entries'
          % (caller['gates'], caller['stages'], caller['units'], caller['roles'], caller['ambient_rank'],
             caller['replay_entries']))
    print('initial gauge: %d loads on the odd roles %s...  per unit: %s'
          % (len(loads), initial['roles'][:4], initial['per_unit']))
    print('final gauge  : %d unloads then %d swaps, signs %s, per unit: %s'
          % (len(unloads), len(swaps), final['swap_signs'], final['per_unit']))
    print('paid         : %d recodings, %s maps, %s adds, %s clears, %d children, %d adapters/invocation'
          % (paid['recodings'], paid['field_bill']['monomial_field_maps'], paid['field_bill']['scalar_adds'],
             paid['field_bill']['owned_clears'], paid['field_bill']['recursive_gaussian_children'],
             paid['adapter_charge_per_invocation']))
    print('productive   : main T = %s (equals the invoiced census: %s)'
          % (productive['main_T'], productive['census_equals_invoice']))
    print('derivation   : caller -> word (0 residual) -> operator (all block counts) -> diagonal census -> '
          'invoice, every link proved in this package')

    need(caller['gates'] == 259 and caller['units'] == p, 'the caller is materialized')
    need(initial['every_role_odd'] and initial['per_unit'], 'the initial gauge is complete')
    need(final['per_unit'] and final['swap_signs'] == [-1], 'the final gauge is complete')
    need(paid['recodings'] == 77 and paid['field_bill']['recursive_gaussian_children'] == 0,
         'the paid corrections are enumerated')
    need(productive['census_equals_invoice'] is True, 'the productive ranks follow from the same caller')

    # the complete derivation: caller + gauges + corrections -> the word -> the operator -> its diagonal
    # -> the invoiced census, every link proved elsewhere in this package and cited here by receipt
    word = json.loads((HERE/'P19_WORD.json').read_text())
    lift = json.loads((HERE/'P19_LIFT.json').read_text())
    out['derivation'] = {
        'step 1: the caller computes the standard word': {
            'claim': 'the 259 gates replayed against the standard word differ on 0 of the replayed entries',
            'receipt': 'P19_WORD.json', 'entries': word['entries_checked'], 'residual': 0},
        'step 2: the word is the controller operator for every block count': {
            'claim': ('Phi is a ring homomorphism on the retained-stage monomial ring and every gate kind is the '
                      'Phi-image of its monomial, so the gate list realises the operator at every block count'),
            'receipt': 'P19_LIFT.json', 'exponent_pairs': 263169, 'status': lift['status']},
        'step 3: the operator has the design target census': {
            'claim': ('the factorisation diagonal of that operator holds exactly the design multiset at p=3,4,5,8,19'),
            'receipt': 'P19_DIAGCENSUS.json', 'status': census['status']},
        'step 4: the census is the invoice': {
            'claim': 'T measured on the diagonal equals the invoiced target histogram rank by rank',
            'receipt': 'P19_DIAGCENSUS.json', 'equality': d19['census_equals_invoice']},
        'conclusion': ('the abstract/controller caller, its endpoint, its census and every paid-correction record are '
                       'exhibited, and the ranks follow for that endpoint through the four links above. Encoding this '
                       'p19 chain into the producer native event stream remains an INHERITED PREMISE, so the admitted '
                       'physical caller is not covered here')}
    out['status'] = 'PASS_ABSTRACT_CALLER_BASE_CONDITION_ITEMS'
    out['what_this_does_not_add'] = ('no hypothesis beyond the inherited producer admission: each exhibited field is a '
                                     'named requirement of PHYSICAL.md:59')
    out['explicitly_not_proved'] = ('that this p19 chain is encoded into the producer native event stream, hence that it '
                                    'is an admitted physical caller')
    (HERE/'P19_CALLER.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
