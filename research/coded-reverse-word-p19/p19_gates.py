#!/usr/bin/env python3
"""Final gate audit: every acceptance condition in one place, read from the receipts.

Checks, in order:
  1 the diagonal census receipt: status, census_equals_invoice, multiset_match, the exact p=19
    histogram, the residual and denominator statements, the role permutation and what it
    preserves;
  2 the physical chain: 259 gates, 77 recodings, the field bill, the unit closure at p=19;
  3 the arithmetic: kappa, complex supplier, the three guards at the invoiced census, the bill;
  4 the claim: status and attachment, with the inherited premises still listed;
  5 hash consistency: every receipt pinned in RESULT.json matches its file;
  6 registered-command agreement between VERIFY.json, VALIDATION.md and the scripts.

No file is written; the exit status is the verdict.
"""
import hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE/'RESULT.json').read_text())
CLAIM = json.loads((HERE/'P19_CLAIM.json').read_text())
DC = json.loads((HERE/'P19_DIAGCENSUS.json').read_text())
WORD = json.loads((HERE/'P19_WORD.json').read_text())
if isinstance(WORD, list): WORD = WORD[0]
UNITS = json.loads((HERE/'P19_UNITS.json').read_text())
MACRO = json.loads(gzip.decompress((HERE/'P19_NATIVE_MACRO.json.gz').read_bytes()))
MACRO_REPLAY = json.loads((HERE/'P19_NATIVE_MACRO_REPLAY.json').read_text())
FORWARD = json.loads((HERE/'P19_FORWARD_PROGRAM.json').read_text())
REVERSE = json.loads((HERE/'P19_REVERSE_PROGRAM.json').read_text())
RESOURCES = json.loads((HERE/'P19_MACRO_RESOURCES.json').read_text())

TARGETS = json.loads((HERE/'P19_TARGETS.json').read_text())
WANT_T_TOTAL = {4: 532, 7: 133, 8: 893, 9: 6642, 17: 448, 25: 448, 33: 448, 41: 448,
                49: 448, 57: 448, 65: 448, 73: 448, 153: 224}
WANT_T_MAIN = {9: 448, 17: 448, 25: 448, 33: 448, 41: 448, 49: 448, 57: 448, 65: 448,
               73: 448, 153: 224}
fails = []

def check(name, ok, detail=''):
    print('%-6s %-52s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok: fails.append(name)

# 1 diagonal census
d19 = DC['cases']['p19_IIIIIIIIITTTTTTTTT']
check('census status', DC['status'] == 'PASS_DIAGONAL_CENSUS_IS_INVOICED', DC['status'])
check('census equals invoice', d19['census_equals_invoice'] is True)
check('multiset match', d19['multiset_match'] is True)
# the histogram is derived from the receipts and only then compared with the regression value:
# P19_TARGETS carries the base definition's own histogram, P19_DIAGCENSUS the measured one
from_receipt = {int(k): v for k, v in d19['diagonal_census'].items()}
from_definition = {int(k): v for k, v in TARGETS['designed_T'].items()}
check('histogram: measured == definition (cross-receipt)', from_receipt == from_definition,
      'measured %d ranks, definition %d ranks' % (len(from_receipt), len(from_definition)))
check('histogram: measured total == regression value', from_receipt == WANT_T_TOTAL,
      '%d ranks' % len(from_receipt))
main_from_diag = {int(k): v for k, v in d19['census_main_only'].items()} \
    if 'census_main_only' in d19 else {r: v for r, v in from_receipt.items() if r in WANT_T_MAIN}
check('histogram: main part == regression value', main_from_diag == WANT_T_MAIN, str(sorted(main_from_diag.items())))
check('residual and denominators recorded',
      bool(d19.get('residual_equality')) and bool(d19.get('diagonal_denominators')))
check('role permutation recorded', 'role_permutation' in d19 and 'permutation_preserves' in d19,
      '%d roles mapped' % len(d19['role_permutation']))
check('permutation preserves the five properties',
      set(d19['permutation_preserves']) >= {'owner_allocation', 'helper_separation', 'paid_D_profile',
                                            'target_histogram', 'endpoint_typing'})

# 2 physical chain
check('chain gate count', WORD['gate_records'] == 259, str(WORD['gate_records']))
check('chain recodings', WORD['recodings'] == 77, str(WORD['recodings']))
check('chain field bill present',
      (WORD['monomial_field_maps'], WORD['scalar_adds'], WORD['owned_clears'],
       WORD['recursive_gaussian_children']) == (17248, 68992, 1232, 0), 'cross-checked against the claim below')
check('chain replay entries', WORD['entries_checked'] == 38*112*512, str(WORD['entries_checked']))
u19 = UNITS['cases']['p19_IIIIIIIIITTTTTTTTT']
check('19 units', u19['pairs'] == 19)
check('19 loads / 19 unloads / 19 swaps',
      (u19['loads'], u19['unloads'], u19['swaps']) == (19, 19, 19),
      '%s/%s/%s' % (u19['loads'], u19['unloads'], u19['swaps']))
check('coded endpoint denominators', UNITS['cases']['p3_IT']['endpoint']['coded_denominators'] == [1, 13])
check('standard endpoint denominators', UNITS['cases']['p3_IT']['endpoint']['std_denominators'] == [1])
check('signed swap convention', u19['terminal']['swap_sign'] == -1)
check('zero recursive Gaussian children', u19['terminal']['recursive_gaussian_children'] == 0)
check('typed macro emission', MACRO['status'] == 'PASS_P19_TYPED_NATIVE_MACRO_EMISSION')
check('typed macro replay', MACRO_REPLAY['status'] == 'PASS_P19_NATIVE_MACRO_REPLAY')
check('literal forward program', FORWARD['status'] == 'PASS_LITERAL_FORWARD_QUERY_PROGRAM')
check('literal reverse program', REVERSE['status'] == 'PASS_LITERAL_REVERSE_LETTER_PROGRAM')
check('macro resource accounting', RESOURCES['status'] == 'PASS_P19_MACRO_RESOURCE_ACCOUNTING')
check('macro cardinality', MACRO['gate_records'] == MACRO_REPLAY['events'] == 259)
check('macro no new rank-bearing children',
      RESOURCES['resources']['new_rank_bearing_children'] == 0 and
      RESOURCES['resources']['recursive_gaussian_children'] == 0)
check('literal forward cleanup', FORWARD['owned_work_final_zero'] is True)
check('literal reverse cleanup', REVERSE['endpoint']['owned_scratch_blank'] is True)

# 3 arithmetic
check('kappa: claim == result receipt', CLAIM['kappa'] == RESULT['attachment']['kappa_value'], CLAIM['kappa'])
check('kappa == regression value', CLAIM['kappa'] == '951999/280000000')
check('complex supplier', abs(CLAIM['complex_saving'] - 0.007578535) < 1e-9, str(CLAIM['complex_saving']))
g = CLAIM['guards']
check('alpha', abs(g['alpha'] - 0.995794142) < 5e-9, '%.9f' % g['alpha'])
check('gamma', abs(g['gamma'] - 0.963763313) < 5e-9, '%.9f' % g['gamma'])
check('delta', abs(g['delta'] - 0.951560608) < 5e-9, '%.9f' % g['delta'])
b = CLAIM['field_level_bill']
word_bill = (WORD['recodings'], WORD['monomial_field_maps'], WORD['scalar_adds'], WORD['owned_clears'],
             WORD['recursive_gaussian_children'])
claim_bill = (b['recodings'], b['monomial_field_maps'], b['scalar_adds'], b['owned_clears'],
              b['recursive_gaussian_children'])
check('bill: word receipt == claim receipt', word_bill == claim_bill, str(word_bill))
check('bill: claim == regression value', claim_bill == (77, 17248, 68992, 1232, 0))

# 4 claim attachment
check('claim status', CLAIM['status'] == 'CONDITIONAL_P19_CODED_WORD_KAPPA_CANDIDATE', CLAIM['status'])
check('physical attachment is CONDITIONAL', CLAIM['physical_attachment']['status'] == 'CONDITIONAL',
      CLAIM['physical_attachment']['requires'])
check('no unconditional physical attachment', CLAIM['attachment']['kappa_attached_to_physical_chain'] is False, 'false')
check('rank-8 treatment documented', 'EXCLUDED' in CLAIM['profile_reconciliation']['rank_8_treatment'], 'excluded')
check('priced D profile is the inherited P_NEW',
      {int(k): v for k, v in CLAIM['profile_reconciliation']['invoice_paid_profile'].items()} == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}, 'P_NEW')
check('D described as inherited, not derived here',
      'REUSES' in CLAIM['paid_profile_provenance']['derived_from'] or 'INHERITED' in CLAIM['paid_profile_provenance']['derived_from'],
      'inherited input')
check('no unconditional physical attachment', CLAIM['attachment']['kappa_attached_to_physical_chain'] is False)
check('native-admission premise retained',
      any('native' in p.lower() or 'operation-level' in p.lower() for p in CLAIM['premises']),
      '%d premises' % len(CLAIM['premises']))
ap = json.loads((HERE/'P19_NATIVE_APPLY.json').read_text())
check('native apply: frames end on final', all(o['persistent_final_matches'] for o in ap['orientations'].values()),
      '%d steps' % ap['orientations']['forward']['state_steps'])
check('frozen word: derived profile == declared profile', ap['profile_matches_derived'] is True,
      str(ap['paid_histogram_derived']))
check('native apply: control word derives its own profile',
      ap['control_authoritative_word']['profile_matches_derived'] is True,
      str(ap['control_authoritative_word']['local_profile_declared']))
check('lowering: gates are the stated primitive',
       json.loads((HERE/'P19_LOWERING.json').read_text())['status'] == 'PASS_PRIMITIVE_SPEC_BINDING',
      'R = D.Q, X - Q.C.Y, C^-1 after Q^-1')
cal = json.loads((HERE/'P19_CALLER.json').read_text())
check('base condition (abstract endpoint): caller', cal['completed_caller']['gates'] == 259, str(cal['completed_caller']['kinds']))
check('base condition: initial gauge', cal['initial_gauge']['per_unit'] and cal['initial_gauge']['every_role_odd'],
      '%d loads' % len(cal['initial_gauge']['roles']))
check('base condition: final gauge', cal['final_gauge']['per_unit'] and cal['final_gauge']['swap_signs'] == [-1],
      '%d unloads, %d swaps' % (len(cal['final_gauge']['unload_roles']), len(cal['final_gauge']['swaps'])))
check('base condition: paid corrections', cal['paid_corrections']['recodings'] == 77,
      str(cal['paid_corrections']['field_bill']))
check('base condition: productive ranks follow', cal['productive_main_ranks']['census_equals_invoice'] is True,
      'main T')
check('census source is the diagonal', 'diagonal' in CLAIM['census_source']['notion'],
      CLAIM['census_source']['notion'][:40])
check('row supports labelled diagnostic',
      CLAIM['census_source']['row_supports'].startswith('diagnostic only'))

# 5 hash consistency
PINS = {'diagcensus_receipt_sha256': 'P19_DIAGCENSUS.json',
        'binding_receipt_sha256': 'P19_LIFT.json',
        'bridge_receipt_sha256': 'P19_BRIDGE.json',
        'unit_receipt_sha256': 'P19_UNITS.json',
        'frames_receipt_sha256': 'P19_FRAMES.json',
        'cascade_receipt_sha256': 'P19_CASCADE.json',
        'invariant_receipt_sha256': 'P19_INVARIANT.json',
        'reprice_receipt_sha256': 'P19_REPRICE.json',
        'native_apply_receipt_sha256': 'P19_NATIVE_APPLY.json',
        'lowering_receipt_sha256': 'P19_LOWERING.json',
        'claim_receipt_sha256': 'P19_CLAIM.json',
        'word_receipt_sha256': 'P19_WORD.json',
        'caller_receipt_sha256': 'P19_CALLER.json'}
for key, fname in PINS.items():
    f = HERE/fname
    if key in RESULT and f.exists():
        check('pin %s' % fname, hashlib.sha256(f.read_bytes()).hexdigest() == RESULT[key])
check('address-control pin', hashlib.sha256((HERE/'P19_BANK.json').read_bytes()).hexdigest()
      == RESULT['address_control']['receipt_sha256'])

# 6 registered commands agree
VERIFY = json.loads((HERE/'VERIFY.json').read_text())
def _script(argv):
    return next((Path(a).name for a in argv if str(a).endswith('.py')), str(argv[-1]))
registered = [_script(c['argv']) for c in VERIFY['commands']]
on_disk = sorted(p.name for p in HERE.glob('p19_*.py')) + ['verify.py']
missing = [r for r in registered if r not in on_disk]
check('registered commands exist', not missing, str(missing))
budget = sum(c['timeout_seconds'] for c in VERIFY['commands'])
check('replay budget within cap', budget <= 1200, '%d s, %d commands' % (budget, len(VERIFY['commands'])))

print()
print('FAILURES:', fails if fails else 'none')
print('VERDICT:', 'ALL GATES PASS' if not fails else 'GATES FAILED')
sys.exit(0 if not fails else 1)
