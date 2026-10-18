#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact boundary and unmodified native replay; standard library only.
conorholds, with substantial OpenAI Codex assistance.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import (add_price, construct, dual, load, price, require, sha, splice, strict_json)
from cleanup import construct_cleanup, factor_block, operator
from comparison import compare, method_baselines


def panel_replay(gates, n, primitives=False, frame=0):
    work = n + 8
    state = [{r: Q(1)} for r in range(work + 1)]
    count = 0
    def add(t, s, q):
        require(t != s, 'aliased replay add')
        for col, x in list(state[s].items()):
            y = state[t].get(col, Q(0)) + q*x
            if y:
                state[t][col] = y
            else:
                state[t].pop(col, None)
    def scale(t, q):
        state[t] = {col: q*x for col, x in state[t].items()}
    for gate in gates:
        require(gate[-1] == frame, 'unexpected boundary frame')
        require(type(gate[1]) is int and 0 <= gate[1] < n, 'boundary target')
        if gate[0] == 'scale':
            q = Q(gate[2], gate[3]); price(gate)
            scale(gate[1], q); count += price(gate)
            continue
        require(gate[0] == 'add' and type(gate[2]) is int and 0 <= gate[2] < n, 'boundary source')
        t, s, num, den = gate[1:5]; q = Q(num, den)
        require(q != 0 and den > 0 and den & (den-1) == 0, 'boundary coefficient')
        if not primitives:
            add(t, s, q); count += price(gate)
            continue
        state[work] = {}; count += 2
        for i, bit in enumerate(bin(abs(q.numerator))[2:]):
            if i:
                scale(work, Q(2)); count += 2
            if bit == '1':
                add(work, s, Q(1)); count += 2
        for _ in range(q.denominator.bit_length()-1):
            scale(work, Q(1, 2)); count += 2
        add(t, work, Q(1 if q > 0 else -1)); count += 2
        state[work] = {}; count += 2
    return state, count


def panel_checks(word, recipe, gates, report, prep):
    n = 2*word['v'] + word['R']; controls = []
    references = {}
    for back in (False, True):
        old = [dual(e) for e in word['compensation']] if back else word['compensation']
        new = [dual(e) for e in gates] if back else gates
        reference, _ = panel_replay(old, n)
        result, charged = panel_replay(new, n, primitives=True)
        require(result[:n] == reference[:n], 'arbitrary-input boundary endpoint')
        require(not result[n+8] and all(result[i] == {i: Q(1)} for i in range(n, n+8)), 'private boundary state')
        require(charged == report['after_real'], 'literal Horner/scale charge')
        references[back] = reference[:n]
    mutants = {}
    mutants['omit_preparation'] = gates[1:]
    mutants['omit_restoration'] = gates[:-1]
    mutant = copy.deepcopy(gates)
    index = next(i for i in range(len(prep), len(gates)-len(prep)) if mutant[i][0] == 'add')
    mutant[index][3] *= -1; mutants['wrong_middle_sign'] = mutant
    mutant = copy.deepcopy(gates)
    index = next(i for i, e in enumerate(prep) if e[0] == 'scale')
    mutant[index][2], mutant[index][3] = mutant[index][3], mutant[index][2]
    mutants['wrong_scale_reciprocal'] = mutant
    mutants['restoration_in_preparation_order'] = gates[:-len(prep)] + list(reversed(gates[-len(prep):]))
    for name, mutant in mutants.items():
        result, _ = panel_replay(mutant, n)
        require(result[:n] != references[False], 'accepted semantic control: ' + name)
        controls.append(name)
    reversed_dual = list(reversed([dual(e) for e in gates]))
    require(panel_replay(reversed_dual, n)[0][:n] != references[True], 'accepted reversed dual chronology')
    controls.append('reversed_dual_chronology')
    bad = copy.deepcopy(gates); bad[0][-1] = 1
    try:
        panel_replay(bad, n)
    except ValueError:
        controls.append('nonzero_boundary_frame')
    else:
        raise ValueError('accepted nonzero boundary frame')
    mutations = {}
    bad = copy.deepcopy(recipe); bad['claimed']['after_real'] -= 16
    mutations['understated_claimed_basis_price'] = (bad, 'complete paid recipe counts')
    bad = copy.deepcopy(recipe); bad['operations'][0][2] = bad['operations'][0][1]
    mutations['aliased_basis_shear'] = (bad, 'shear operand range or alias')
    bad = copy.deepcopy(recipe); bad['operations'][0][1] = True
    mutations['boolean_basis_operand'] = (bad, 'basis operation types')
    bad = copy.deepcopy(recipe); bad['operations'][0][4] = 3
    mutations['nondyadic_basis_coefficient'] = (bad, 'basis alphabet')
    bad = copy.deepcopy(recipe); bad['sources'][0] = 0
    mutations['changed_active_helper_inventory'] = (bad, 'all original compensation helpers')
    for name, (mutation, error) in mutations.items():
        try:
            construct(word, mutation)
        except ValueError as exc:
            require(error in str(exc), 'recipe control missed intended guard: '+name)
            controls.append(name)
        else:
            raise ValueError('accepted recipe control: ' + name)
    bad_word = copy.deepcopy(word); bad_word['start'][recipe['sources'][0]] = 1
    try:
        construct(bad_word, recipe)
    except ValueError as exc:
        require(str(exc) == 'ineligible helper', 'helper eligibility control missed intended guard')
        controls.append('nonzero_entry_frame_helper')
    else:
        raise ValueError('accepted ineligible helper')
    return dict(all_logical_columns=n, affected_columns=word['v']+len(recipe['sources']),
                orientations=2, private_centres_untouched=8, arbitrary_coefficient_work_cleared=True,
                literal_real_primitives=report['after_real'], negative_controls=controls)


def cleanup_checks(word, gates, counts):
    n = 2*word['v']+word['R']; controls = []
    for backward in (False, True):
        old = [dual(g) for g in word['cleanup']] if backward else word['cleanup']
        new = [dual(g) for g in gates] if backward else gates
        expected, _ = panel_replay(old, n, frame=1)
        actual, paid = panel_replay(new, n, primitives=True, frame=1)
        require(actual[:n] == expected[:n] and not actual[n+8]
                and actual[n:n+8] == expected[n:n+8] and paid == counts['after_real'],
                'cleanup both literal primitive boundaries and prices')
    expected = operator(word, word['cleanup'])
    mutations = {'omit_cleanup_first_gate': gates[1:], 'omit_cleanup_last_gate': gates[:-1]}
    wrong = copy.deepcopy(gates); wrong[0][3] *= -1
    mutations['wrong_cleanup_shear_sign'] = wrong
    for name, changed in mutations.items():
        require(operator(word, changed) != expected, 'accepted cleanup endpoint control: '+name)
        controls.append(name)
    old_back = panel_replay([dual(g) for g in gates], n, frame=1)[0]
    wrong_back = panel_replay(list(reversed([dual(g) for g in gates])), n, frame=1)[0]
    require(old_back[:n] != wrong_back[:n], 'accepted cleanup reversed dual chronology')
    controls.append('cleanup_reversed_dual_chronology')
    for name, change in [('cleanup_wrong_frame', lambda e: e.__setitem__(-1, 0)),
                         ('cleanup_operand_alias', lambda e: e.__setitem__(2, e[1]))]:
        wrong = copy.deepcopy(gates); change(wrong[0])
        try:
            operator(word, wrong)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted cleanup contract control: '+name)
    recipe = strict_json((HERE / 'CLEANUP-RECIPE.json').read_bytes())
    mutants = {}
    wrong = copy.deepcopy(recipe); wrong['claimed']['after_real'] -= 2
    mutants['underpaid_cleanup'] = wrong
    wrong = copy.deepcopy(recipe); wrong['blocks'][0]['pivots'][0][0] = n
    mutants['out_of_range_cleanup_pivot'] = wrong
    wrong = copy.deepcopy(recipe); wrong['blocks'][0]['registers'][0] = word['v']
    mutants['cleanup_target_in_block'] = wrong
    wrong = copy.deepcopy(recipe); wrong['original_cleanup_sha256'] = '0'*64
    mutants['stale_cleanup_input_binding'] = wrong
    for name, wrong in mutants.items():
        try:
            construct_cleanup(word, wrong)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('accepted cleanup recipe control: '+name)
    fixture_word = {'v': 1, 'R': 2, 'final': [1]*4}
    fixture = [{0: Q(1), 2: Q(1)}, {1: Q(1)}, {0: Q(1), 2: Q(-1)}, {3: Q(1)}]
    fixture_gates = factor_block(fixture, [0, 2], [[0, 2], [2, 0]])
    require(operator(fixture_word, fixture_gates) == fixture, 'signed permutation/determinant-two fixture')
    return dict(counts=counts, all_logical_columns=n, orientations=2,
                literal_primitives_checked=True, negative_controls=controls,
                signed_permutation_fixture=True)


def live_sources(root, pins):
    sources = strict_json((HERE / 'SOURCES.json').read_bytes())
    for row in sources['files']:
        if row['usage'] == 'input':
            require(sha((root / row['path']).read_bytes()) == row['sha256'], 'live source: ' + row['path'])
    archive = root / 'research/community-frontier1094-audit/selected-replay.tar.gz'
    with tarfile.open(archive) as handle:
        for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json'):
            member = 'candidate/strict/global/base/providers/gauge44/' + name
            require(sha(handle.extractfile(member).read()) == pins[name], 'selected export: ' + name)
    return dict(status='PASS_LIVE_SELECTED_ARCHIVE_AND_SOURCE_PINS', source_files=len(sources['files']))


def native_checks(word, gates, cleanup, predicted, old_checks, report, output):
    require(not output.exists(), 'native output already exists')
    output.mkdir(parents=True)
    changed = copy.deepcopy(word); changed['compensation'] = gates
    changed['cleanup'] = cleanup
    encoded = json.dumps(changed, sort_keys=True, separators=(',', ':')).encode()
    (output / 'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(encoded, mtime=0))
    env = os.environ.copy(); env.pop('PYTHONOPTIMIZE', None)
    for name in ('native_emitter.py', 'native_auditor.py'):
        with (output / (name + '.log')).open('w') as log:
            subprocess.run([sys.executable, '-I', '-B', str(HERE / 'reference' / name), str(output)],
                           check=True, stdout=log, stderr=subprocess.STDOUT, env=env, timeout=240)
        print('PASS unchanged ' + name, flush=True)
    programs = strict_json(gzip.decompress((output / 'LOCAL-PROGRAMS.json.gz').read_bytes()))
    checks = strict_json((output / 'LOCAL-CHECKS.json').read_bytes())
    audit = strict_json((output / 'INDEPENDENT-LOCAL-REPLAY.json').read_bytes())
    require(programs == predicted, 'native emission versus independently spliced stream')
    counts = {}
    for orientation in ('forward', 'backward'):
        row = checks[orientation]; old = old_checks[orientation]
        require(row['paid_profile'] == old['paid_profile'] == word['local_profile'], 'changed recursive profile')
        require(row['scalar_macros'] == old['scalar_macros']-report['before_macros']+report['after_macros'], 'full scalar macro charge')
        require(row['real_component_primitive_bound'] == old['real_component_primitive_bound']-report['saving_real'], 'full scalar primitive charge')
        require(audit['local'][orientation]['prefix_bits_upper'] <= 192, 'local prefix allowance')
        counts[orientation] = dict(before_macros=old['scalar_macros'], after_macros=row['scalar_macros'],
                                  before_real=old['real_component_primitive_bound'], after_real=row['real_component_primitive_bound'],
                                  prefix_l1_upper=audit['local'][orientation]['prefix_l1_upper'],
                                  prefix_bits_upper=audit['local'][orientation]['prefix_bits_upper'],
                                  paid_profile=row['paid_profile'], all_columns=row['all_columns'],
                                  program_sha256=row['sha256'])
    compiler = 64*74**3; children = sum(word['local_profile'].values()); n = 2*word['v']+word['R']
    def bill(macros, real):
        adapters = 16*(macros+children+n+len(word['centers'])) + 64*73
        return dict(local_adapters=adapters, compiler=compiler, scalar_and_compiler_bound=adapters*compiler+real)
    before = bill(max(r['scalar_macros'] for r in old_checks.values()), max(r['real_component_primitive_bound'] for r in old_checks.values()))
    after = bill(max(r['scalar_macros'] for r in checks.values()), max(r['real_component_primitive_bound'] for r in checks.values()))
    require(after['scalar_and_compiler_bound'] < before['scalar_and_compiler_bound'], 'no complete local bill gain')
    return dict(orientations=counts, native_negative_controls=audit['negative_controls_rejected'],
                all_non_scalar_events_unchanged=True, source_helpers=word['R'],
                candidate_word_payload_sha256=sha(encoded), local_bill_before=before, local_bill_after=after,
                bill_scope='Exact selected local scalar/compiler formula only; no changed global invoice, hosting, phase lowering or outer admission.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path)
    parser.add_argument('--panel-only', action='store_true', help='boundary/price/controls only; no native full-word replay')
    parser.add_argument('--out', type=Path, help='fresh directory retaining native words/logs')
    parser.add_argument('--record', type=Path, help='write a new receipt, refusing existing paths')
    args = parser.parse_args()
    word, recipe, programs, checks, pins = load()
    gates, counts, prep, _ = construct(word, recipe)
    require(gates == strict_json((HERE / 'COMPENSATION.json').read_bytes()), 'literal compensation witness')
    cleanup, cleanup_counts = construct_cleanup(word)
    require(cleanup == strict_json((HERE / 'CLEANUP.json').read_bytes()), 'literal cleanup witness')
    cleanup_receipt = cleanup_checks(word, cleanup, cleanup_counts)
    changes = {key: counts[key]+cleanup_counts[key] for key in
               ('before_macros', 'after_macros', 'before_real', 'after_real', 'saving_real')}
    predicted = splice(word, programs, gates, cleanup)
    panel = panel_checks(word, recipe, gates, counts, prep)
    comparison = compare(word, programs, predicted, args.upstream.resolve() if args.upstream else None)
    forest_recipe = strict_json((HERE / 'FOREST-RECIPE.json').read_bytes())
    require(forest_recipe['word_sha256'] == recipe['word_sha256'], 'forest source binding')
    for kind in ('T', 'H'):
        parents = {}
        order = []
        for tag, a, b, numerator, denominator in forest_recipe['operations']:
            require(tag in ('T', 'H') and numerator in (-1, 1) and denominator == 1,
                    'signed-unit forest alphabet')
            if tag == kind:
                child, parent = (a, b) if tag == 'T' else (b, a)
                require(child not in parents, 'multiple forest parents')
                parents[child] = parent; order.append(child)
        positions = {child: i for i, child in enumerate(order)}
        for child, parent in parents.items():
            if parent in positions:
                require(positions[child] < positions[parent], 'forest cycle or non-leaf-first order')
    forest_gates, forest_counts, _, _ = construct(word, forest_recipe)
    require(forest_gates == strict_json((HERE / 'FOREST-COMPENSATION.json').read_bytes()), 'literal forest witness')
    for backward in (False, True):
        old = [dual(e) for e in word['compensation']] if backward else word['compensation']
        forest = [dual(e) for e in forest_gates] if backward else forest_gates
        expected = panel_replay(old, 2*word['v']+word['R'])[0]
        actual, cost = panel_replay(forest, 2*word['v']+word['R'], primitives=True)
        require(actual[:704] == expected[:704] and not actual[712]
                and cost == forest_counts['after_real'], 'same-input forest boundary and complete charge')
    methods = method_baselines(word, programs, forest_gates, cleanup, gates,
                               args.upstream.resolve() if args.upstream else None)
    print('PASS restored boundary: all arbitrary columns, both orientations and controls', flush=True)
    binding = live_sources(args.upstream.resolve(), pins) if args.upstream else {'status': 'NOT_RUN_LIVE_UPSTREAM_BINDING'}
    result = dict(status='PASS_COMPLEX_COMPENSATION_NETWORK', source_payload_sha256=recipe['word_sha256'],
                  counts=counts, panel=panel, cleanup=cleanup_receipt, total_changes=changes,
                  forest_comparison=forest_counts, merged_gauge_comparison=comparison,
                  matched_method_comparison=methods, selected_kappa_unchanged=True)
    if not args.panel_only:
        if args.out:
            result['native'] = native_checks(word, gates, cleanup, predicted, checks, changes, args.out.resolve())
        else:
            with tempfile.TemporaryDirectory(prefix='complex-comp-network-') as tmp:
                result['native'] = native_checks(word, gates, cleanup, predicted, checks, changes, Path(tmp) / 'native')
    if args.record:
        require(not args.panel_only, 'record needs complete native replay')
        with args.record.open('x') as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    elif not args.panel_only:
        require(result == strict_json((HERE / 'CERTIFICATE.json').read_bytes()), 'recorded native certificate mismatch')
    else:
        certificate = strict_json((HERE / 'CERTIFICATE.json').read_bytes())
        require(result['counts'] == certificate['counts'] and result['panel'] == certificate['panel']
                and result['cleanup'] == certificate['cleanup'] and result['total_changes'] == certificate['total_changes']
                and result['forest_comparison'] == certificate['forest_comparison']
                and result['matched_method_comparison'] == certificate['matched_method_comparison']
                and result['merged_gauge_comparison'] == certificate['merged_gauge_comparison'], 'panel certificate mismatch')
    print(json.dumps({'status': result['status'], 'counts': counts, 'live_binding': binding,
                      'native': 'NOT_RUN' if args.panel_only else 'PASS_FULL_WORD'}, sort_keys=True))


if __name__ == '__main__':
    main()
