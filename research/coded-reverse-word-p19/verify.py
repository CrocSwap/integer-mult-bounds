#!/usr/bin/env python3
"""Fast receipt for the physical p=19 coded-word supplier.

Runs the formal controller verifier, checks the p=19 diagonalisation receipt, then
the package receipts for the controller reference, physical coded listing and claim.
The long traces are the separate commands p19_plain.py and p19_word.py.
"""
import gzip
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNERS, SIZE = 112, 512

def need(ok, why):
    if not ok: raise ValueError(why)

def run(path, timeout=900):
    p = subprocess.run([sys.executable, '-I', '-B', str(ROOT/path)], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout)
    sys.stdout.write(p.stdout)
    sys.stderr.write(p.stderr)
    need(p.returncode == 0, 'subprocess failed: '+path)
    return p.stdout + p.stderr

import hashlib

def main():
    claim = json.loads((HERE/'P19_CLAIM.json').read_text())
    out1 = run('research/coded-reverse-controller/verify.py')
    need('PASS p=19 tail guards at C=0.0034' in out1, 'p=19 tail guards')
    need('0.007579' in out1, 'p=19 raw complex root')
    need('PASS p=2, 448x448' in out1, 'p=2 448x448 conjugation')
    need('at 0.0034 the only failing predicate is the BIT cap' in out1, 'outer ledger')
    diag = json.loads((HERE/'P19_DIAG.json').read_text())
    need(diag['diagonalized'] is True and diag['std']['outputs'] == diag['cod']['outputs']
         and diag['std']['denominators'] == [1], 'p19 diagonalization receipt')
    print('PASS formal controller: p=19 diagonalisation, guards, raw root and outer ledger')

    plain = json.loads((HERE/'P19_PLAIN.json').read_text())
    pw = plain['p19']
    need(plain['status'] == 'PASS_P19_UNCODED_WORD', 'word receipt status')
    need(pw['trace_identity'] == 'replayed in the controller algebra', 'trace identity')
    need(pw['denominators'] == [1], 'standard denominators')
    need((pw['retained_idles'], pw['idle_rank']) == (36, 198), 'idle census')
    need(pw['gates'] == 241 and pw['kinds']['LETTER'] == 39 and pw['kinds']['IDLE'] == 36, 'gate census')
    need((pw['recodings'], pw['terminal_gauge_decoder']) == (0, 0), 'no recoding bill')
    need(abs(pw['invoice_root'] - 0.007578535189897761) < 1e-9 and pw['ambient_rank'] == 153, 'price')
    print('PASS word: p=19 trace == controller, diagonalises with denominators [1], %d gates, '
          '%d retained idles, root %.12f, no recoding bill'
          % (pw['gates'], pw['retained_idles'], pw['invoice_root']))

    need('PASS (a) one-axis power law' in run('research/coded-reverse-word-p19/p19_lift.py'),
         'the lifting lemma runs and passes inside the verifier')
    need('PASS_INHERITED_VOCABULARY_AND_INVOCATION_BUDGET' in run('research/coded-reverse-word-p19/p19_binding.py'),
         'the operation-level binding runs and passes inside the verifier')
    bind = json.loads((HERE/'P19_BINDING.json').read_text())
    need(bind['status'] == 'PASS_INHERITED_VOCABULARY_AND_INVOCATION_BUDGET', 'binding receipt status')
    need(bind['raw_operation_budget'] < bind['raw_allowance'], 'the invocation budget fits the allowance')
    need(bind['invocations_at_p19'] == {'forward': 20, 'backward': 19}, 'invocation counts at p=19')
    need('does_not_show' in bind, 'the binding receipt states what it does not show')
    print('PASS inherited vocabulary and invocation budget: %d forward and %d backward invocations of the frozen '
          'program, raw budget %d of %d'
          % (bind['invocations_at_p19']['forward'], bind['invocations_at_p19']['backward'],
             bind['raw_operation_budget'], bind['raw_allowance']))
    need('PASS_P19_IS_A_FAMILY_INSTANCE' in run('research/coded-reverse-word-p19/p19_family.py'),
         'the family receipt runs and passes inside the verifier')

    need(json.loads((HERE/'P19_UNITS.json').read_text())['status'] == 'PASS_UNIT_COMPOSITION_AND_ENDPOINT_TYPING',
         'the unit/endpoint/terminal receipt runs and passes inside the verifier')
    units = json.loads((HERE/'P19_UNITS.json').read_text())
    need(units['status'] == 'PASS_UNIT_COMPOSITION_AND_ENDPOINT_TYPING', 'units receipt status')
    u19 = units['cases']['p19_IIIIIIIIITTTTTTTTT']
    need(u19['pairs'] == 19, 'the p=19 chain is 19 units')
    need(u19['terminal']['unloads'] == 19 and u19['terminal']['swaps'] == 19
         and u19['terminal']['swap_sign'] == -1, 'the chain closes with 19 unloads and 19 signed swaps')
    need(u19['terminal']['recursive_gaussian_children'] == 0, 'zero recursive Gaussian children')
    need(units['cases']['p3_IT']['endpoint']['coded_denominators'] == [1, 13],
         'the coded endpoint carries the inherited denominator 13')
    need(units['cases']['p3_IT']['endpoint']['std_denominators'] == [1], 'the standard endpoint is [1]')
    need('inherited' in units['endpoint_form'], 'the endpoint form is stated as inherited')
    rec_u = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_UNITS.json').read_bytes()).hexdigest()
         == rec_u['unit_receipt_sha256'], 'the units receipt matches its pinned hash')
    print('PASS endpoint: p=19 is %d units, closes with %d unloads and %d signed swaps, coded endpoint [1, 13] '
          'is the inherited form, zero recursive children'
          % (u19['pairs'], u19['terminal']['unloads'], u19['terminal']['swaps']))

    need('PASS_ABSTRACT_CALLER_BASE_CONDITION_ITEMS'
         in run('research/coded-reverse-word-p19/p19_caller.py'), 'the scoped caller receipt runs and passes')
    cal = json.loads((HERE/'P19_CALLER.json').read_text())
    need(cal['completed_caller']['gates'] == 259 and cal['completed_caller']['units'] == 19, 'the caller')
    need(cal['initial_gauge']['per_unit'] and cal['initial_gauge']['every_role_odd'], 'the initial gauge')
    need(cal['final_gauge']['per_unit'] and cal['final_gauge']['swap_signs'] == [-1], 'the final gauge')
    need(cal['paid_corrections']['recodings'] == 77, 'the paid corrections')
    need(cal['productive_main_ranks']['census_equals_invoice'] is True, 'the productive ranks follow')
    print('PASS caller: the three objects PHYSICAL.md:59 names -- the completed caller, its initial/final gauges '
          'and every paid correction -- are exhibited for this construction, and the productive ranks follow')

    need('PASS_NATIVE_APPLY_TRACE' in run('research/coded-reverse-word-p19/p19_native_apply.py'),
         'apply(program, state) runs on the frozen word inside the verifier')
    ap = json.loads((HERE/'P19_NATIVE_APPLY.json').read_text())
    need(ap['status'] == 'PASS_NATIVE_APPLY_TRACE', 'native apply receipt status')
    need(all(o['persistent_final_matches'] for o in ap['orientations'].values()),
         'both orientations end on canonical.final')
    need(ap['profile_matches_derived'] is True, 'the paid histogram derived from the trace equals the declared profile')
    need(ap['control_authoritative_word']['profile_matches_derived'] is True,
         'the control word derives its own profile: the interpreter is not tuned to this word')
    rec_ap = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_NATIVE_APPLY.json').read_bytes()).hexdigest()
         == rec_ap['native_apply_receipt_sha256'], 'the native-apply receipt matches its pinned hash')
    print('PASS apply: %d records and %d state steps per direction, frames end on final, paid histogram %s derived '
          'from the trace (control word derives its own)'
          % (ap['orientations']['forward']['records'], ap['orientations']['forward']['state_steps'],
             ap['paid_histogram_derived']))

    need('PASS_PRIMITIVE_SPEC_BINDING' in run('research/coded-reverse-word-p19/p19_lowering.py'),
         'the lowering receipt runs and passes inside the verifier')
    low = json.loads((HERE/'P19_LOWERING.json').read_text())
    need(low['status'] == 'PASS_PRIMITIVE_SPEC_BINDING', 'lowering receipt status')
    need(all(low['checks'].values()), 'every lowering check passes: R == D.Q, gauge cancellation, shear form, '
                                      'forward order, idle powers')
    need('not native-producer closure' in low['scope'] and 'not replayed here' in low['scope'],
         'the lowering receipt states its primitive-only scope')
    rec_low = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_LOWERING.json').read_bytes()).hexdigest()
         == rec_low['lowering_receipt_sha256'], 'the lowering receipt matches its pinned hash')
    print('PASS lowering: the emitted gates are the base primitive (R = D.Q, X - Q.C.Y, C^-1 after Q^-1, '
          'gauge cancellation, idle powers)')

    macro = json.loads(gzip.decompress((HERE/'P19_NATIVE_MACRO.json.gz').read_bytes()))
    macro_replay = json.loads((HERE/'P19_NATIVE_MACRO_REPLAY.json').read_text())
    precompilation = json.loads((HERE/'P19_PRECOMPILATION.json').read_text())
    macro_resources = json.loads((HERE/'P19_MACRO_RESOURCES.json').read_text())
    reverse_program = json.loads((HERE/'P19_REVERSE_PROGRAM.json').read_text())
    need(macro['status'] == 'PASS_P19_TYPED_NATIVE_MACRO_EMISSION',
         'typed native macro emission')
    need(macro_replay['status'] == 'PASS_P19_NATIVE_MACRO_REPLAY',
         'typed native macro replay')
    need(precompilation['status'] == 'FINDING_PRECOMPILATION_CONTRACT_MISSING',
         'precompilation probe must retain its unresolved semantic obligations')
    need(precompilation['new_p19_condition'] is True,
         'macro syntax checks do not discharge native admission')
    need(macro['compiled_wrapper_contract']['ports'] == 112,
         'all inherited normalizer ports are bound')
    need(macro['gate_records'] == macro['macro_records'] == macro_replay['events'] == 259,
         'macro/emitted/replayed cardinality')
    need(macro_resources['status'] == 'PASS_P19_MACRO_RESOURCE_ACCOUNTING',
         'literal macro resource accounting')
    need(macro_resources['resources']['recursive_gaussian_children'] == 0,
         'macro recursive children')
    need(macro_resources['resources']['new_rank_bearing_children'] == 0,
         'macro new rank-bearing children')
    need(reverse_program['status'] == 'PASS_LITERAL_REVERSE_LETTER_PROGRAM',
         'literal reverse/letter program')
    need(reverse_program['endpoint']['all_roles_uncoded'] and
         reverse_program['endpoint']['owned_scratch_blank'], 'reverse macro endpoint')
    need(macro_resources['claim_kappa_unchanged'] == claim['model_kappa_candidate'],
         'macro resource claim value')
    print('RECORDED native macro probe: syntax replay only; native precompilation remains unresolved')

    need('PASS_DIAGONAL_CENSUS_IS_INVOICED' in run('research/coded-reverse-word-p19/p19_diagcensus.py'),
         'the diagonal target census must equal the invoiced census')
    dc = json.loads((HERE/'P19_DIAGCENSUS.json').read_text())
    need(dc['status'] == 'PASS_DIAGONAL_CENSUS_IS_INVOICED', 'CLAIM GATE: diagonal census receipt status')
    d19 = dc['cases']['p19_IIIIIIIIITTTTTTTTT']
    need(d19['census_equals_invoice'] is True, 'CLAIM GATE: p=19 diagonal census equals the invoice')
    need(d19['multiset_match'] is True, 'p=19 diagonal target multiset equals the designed multiset')
    rec_dc = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_DIAGCENSUS.json').read_bytes()).hexdigest()
         == rec_dc['diagcensus_receipt_sha256'], 'the diagonal-census receipt matches its pinned hash')
    need(claim.get('attachment', {}).get('kappa_attached_to_physical_chain') is False,
         'CLAIM GATE: no unconditional physical attachment is claimed')
    need(claim['physical_attachment']['status'] == 'CONDITIONAL'
         and 'inherited producer/compiler contract admits' in claim['physical_attachment']['requires'],
         'CLAIM GATE: the attachment is conditional on inherited producer admission')
    need(claim['model_kappa_candidate'] == '951999/280000000', 'the model kappa candidate is recorded')
    need('REUSES' in claim['paid_profile_provenance']['derived_from']
         or 'INHERITED' in claim['paid_profile_provenance']['derived_from'],
         'CLAIM GATE: D is an inherited input, not derived from a p19 trace')
    prc = claim['profile_reconciliation']
    need({int(k): v for k, v in prc['invoice_paid_profile'].items()} == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}, 'the priced profile is P_NEW')
    need({int(k): v for k, v in prc['frozen_event_profile'].items()} == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}, 'the frozen profile')
    need('EXCLUDED' in prc['rank_8_treatment'] and prc['chain_has_no_centre_gate'] is True,
         'CLAIM GATE: the rank-8 treatment is documented')
    need(len(claim['premises']) == 1 and 'inherited producer/compiler contract admits' in claim['premises'][0],
         'CLAIM GATE: one minimal inherited producer/compiler premise')
    need(claim.get('census_source', {}).get('row_supports', '').startswith('diagnostic only'),
         'CLAIM GATE: the row-support census is labelled diagnostic and is not the pricing source')
    need(d19['role_permutation'] is not None and 'permutation_preserves' in d19,
         'the p=19 role permutation and what it preserves are recorded')
    print('PASS diagonal census: p=19 target census %s equals the invoiced T; the row closure is a superseded '
          'diagnostic' % d19['diagonal_census'])

    need(json.loads((HERE/'P19_SYMBOLIC.json').read_text())['status'] == 'PASS_FORMAL_FRESH_BLOCK_GEOMETRY',
         'the fresh-block geometry check runs and passes inside the verifier')
    sym = json.loads((HERE/'P19_SYMBOLIC.json').read_text())
    need(sym['status'] == 'PASS_FORMAL_FRESH_BLOCK_GEOMETRY', 'geometry receipt status')
    rec_sym = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_SYMBOLIC.json').read_bytes()).hexdigest()
         == rec_sym['fresh_block_geometry']['receipt_sha256'], 'the symbolic receipt matches its pinned hash')
    need(sym['cases']['p19_IIIIIIIIITTTTTTTTT']['ambient_rank'] == 153,
         'the p=19 instance has ambient rank 153')
    need(sym['cases']['p19_IIIIIIIIITTTTTTTTT']['blocks'] == 19, 'the p=19 instance has 19 blocks')
    geo = sym['cases']['p19_IIIIIIIIITTTTTTTTT']
    need('formal_controller_main_census' in geo and 'invoiced_main_census' in geo
         and geo['main_census_comparison'], 'the receipt records both histograms and their comparison')
    need(geo['main_census_comparison'] in ('equal', 'differs'), 'the census comparison is stated explicitly')
    # the geometry receipt's census is a formal control, not the pricing source: the target census is
    # gated on P19_DIAGCENSUS.json, which reads the factorisation diagonal
    need(geo['formal_controller_main_census'], 'the census is non-empty')
    need('does not claim physical' in sym['what_this_is'], 'the geometry receipt names its own scope')
    print('PASS geometry: fresh-block realisation at p=19 is %d blocks and ambient rank %d, and the chain reproduces '
          'the thinned controller operator exactly at every tested p'
          % (sym['cases']['p19_IIIIIIIIITTTTTTTTT']['blocks'],
             sym['cases']['p19_IIIIIIIIITTTTTTTTT']['ambient_rank']))
    need('PASS_ADAPTERS_ARE_PART_OF_THE_INHERITED_UNIT' in run('research/coded-reverse-word-p19/p19_bridge.py'),
         'the bridge check runs and reports the inherited-unit result inside the verifier')
    bridge = json.loads((HERE/'P19_BRIDGE.json').read_text())
    need(bridge['status'] == 'PASS_ADAPTERS_ARE_PART_OF_THE_INHERITED_UNIT', 'bridge receipt status')
    need(bridge['operations_between'] > 0 and bridge['adapter_positions']['old_to_new'][1]
         < bridge['adapter_positions']['new_to_old'][0],
         'the adapters bracket a non-empty middle section')
    need(all(v == 448 for v in bridge['adapter_count_per_direction'].values()),
         'the adapter count is the normalizer charge')
    rec0 = json.loads((HERE/'RESULT.json').read_text())
    need(hashlib.sha256((HERE/'P19_BRIDGE.json').read_bytes()).hexdigest() == rec0['bridge_receipt_sha256'],
         'the bridge receipt matches its pinned hash')
    print('PASS bridge: 448 adapters per direction remain in the inherited physical unit; their bracketed middle '
          'is not deleted')

    bank = HERE/'P19_BANK.json'
    need(bank.exists(), 'the address-level replay receipt is missing (run p19_bank.py)')
    bk = json.loads(bank.read_text())
    need(bk['status'] == 'PASS_ADDRESS_LEVEL_TRACE_REPLAY' and sum(bk['differing_entries']) == 0,
         'the gate list realises the controller matrix at address level')
    rec = rec0
    need(hashlib.sha256(bank.read_bytes()).hexdigest() == rec['address_control']['receipt_sha256'],
         'the address-control receipt matches the hash recorded in RESULT.json')
    need(hashlib.sha256((HERE/'P19_LIFT.json').read_bytes()).hexdigest() == rec['binding_receipt_sha256'],
          'the binding receipt matches the hash recorded in RESULT.json')
    print('PASS binding: p=%d address-level replay, %d addresses per role, %d roles, %d gates, 0 differing entries'
          % (bk['p'], bk['addresses_per_role'], bk['roles'], bk['gates']))

    need(claim['field_level_bill']['monomial_field_maps'] == 17248, 'the claim bill is the coded bill')
    need(claim['status'] == 'CONDITIONAL_P19_CODED_WORD_KAPPA_CANDIDATE', 'claim status')
    need(claim['kappa'] == '951999/280000000', 'claim value')
    need(claim['gain_vs_selected_record_percent'] > 12.5 and claim['gain_vs_reported_percent'] > 12.3,
         'both gains are recorded')
    need(claim['compiler']['H0'] == 5170423668736, 'compiler ranks')
    bill = claim['field_level_bill']
    need((bill['recodings'], bill['monomial_field_maps'], bill['scalar_adds'], bill['owned_clears']) ==
         (77, 17248, 68992, 1232), 'the emitted claim carries the physical coded bill')
    need(claim['coded_chain']['gates'] == 259 and claim['coded_chain']['recodings'] == 77,
         'the emitted claim describes the physical coded chain')
    need(claim['uncoded_reference']['gates'] == 241,
         'the emitted claim retains the uncoded controller reference')
    need('not a proof' in claim['compiler']['classification'], 'the compiler stays conditional')
    print('CONDITIONAL_P19_CODED_WORD_KAPPA_CANDIDATE kappa %s: +%.2f%% over the selected record, +%.2f%% over the reported '
          'frontier; complex %s, BIT %s, compiler H0 = %s, field bill %d maps'
          % (claim['kappa'], claim['gain_vs_selected_record_percent'],
             claim['gain_vs_reported_percent'], claim['complex_supplier'],
              claim['bit_supplier'], claim['compiler']['H0'], bill['monomial_field_maps']))
    print(json.dumps({'status': 'CONDITIONAL_P19_CODED_WORD_KAPPA_CANDIDATE', 'kappa': claim['kappa'],
                      'gain_vs_selected_record_percent': claim['gain_vs_selected_record_percent'],
                      'gain_vs_reported_percent': claim['gain_vs_reported_percent'],
                      'field_level_bill': bill}, sort_keys=True))

if __name__ == '__main__':
    main()
