#!/usr/bin/env python3
"""Cold regeneration, exact native proof obligations, complete costs and controls.

@CubeJerry with substantial OpenAI assistance. Apache-2.0.
Separate independent commands check the transpose, formal caller and physical
normalizers. This program never treats successful hash checking as mathematics.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path
import sys
from construct import construct, regenerate
from linear import HERE, digest, load, main_roles, need, read, replay, source_contract
from pricing import caller_invoice, root_invoice, ordinary_bound, verify_price


def pins():
    manifest = read(HERE / 'SOURCE-PINS.json')
    for row in manifest['files']:
        data = (HERE / row['local']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], ('Retained byte pin', row['local']))
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == row['git_blob'], ('Retained Git blob identity', row['local']))
    return len(manifest['files'])


def compiler_dependency(claim):
    """Bind the retained cap theorem and separate BIT application to this claim.

    Their universal completed physical/stock hypotheses remain proof premises;
    these checks establish numeric applicability and exact source identity.
    """
    module = load(HERE / 'retained/compiler/ambient_bounds.py', 'retained_ambient_bounds')
    geometry = module.verify()
    need(claim['physical_ambient_cap'] == geometry['ambient_cap'] == 153
         and claim['logarithm_power'] == geometry['logarithm_power'] == 2300
         and 0 < Q(claim['tested']) <= Q(geometry['covered_saving_interval'][1]),
         'The actual native uses the independently checked cap/logarithm regime')
    bit = read(HERE / 'retained/compiler/bit-audit/RESULT.json')
    bit_bytes = (HERE / 'retained/retained/bit/FRAGMENT-BIT-ADMISSION.json').read_bytes()
    need(bit['source_pins']['bit/FRAGMENT-BIT-ADMISSION.json']
         == hashlib.sha256(bit_bytes).hexdigest(),
         'The separately reviewed BIT application has the exact inherited source')
    wrapper = bit['wrapper_arithmetic_from_canonical_admission']
    need(len(wrapper) == 2 and Q(wrapper[0]['previous']) == Q('0.0034')
         and Q(wrapper[-1]['admitted']) == Q('0.00376669'),
         'Separate BIT completed-backend chain and saving are source-bound')
    return dict(actual_ambient=geometry['ambient_cap'],
                logarithm_power=geometry['logarithm_power'],
                bit_source_sha256=hashlib.sha256(bit_bytes).hexdigest(),
                bit_ordinary_saving=wrapper[-1]['admitted'])


def allocation(word, caller):
    helper_roles = sorted(set(range(word['public'])) - main_roles(word))
    whole_helpers = set()
    calls = 0
    for event in caller['events']:
        if event[0] != 'HOST2':
            continue
        stage, x, y, x2, y2 = event[1:]
        need(len({x, y, x2, y2}) == 4 and all(0 <= r < caller['roles'] for r in (x, y, x2, y2)),
             'Four distinct caller main fields')
        assigned = {}
        for i, port, j, k in zip(word['live'], word['ports'], word['hosted']['X2'], word['hosted']['Y2']):
            assigned[i] = ('main', x, port)
            assigned[i + 112] = ('main', y, port)
            assigned[j] = ('main', x2, port)
            assigned[k] = ('main', y2, port)
        for role in helper_roles:
            assigned[role] = ('helper', calls, role)
            whole_helpers.add(assigned[role])
        need(set(assigned) == set(range(word['public']))
             and len(set(assigned.values())) == word['public'],
             'Injective public allocation: every added field is independent')
        # The 51 owned slots may be reused only between calls, after exact
        # replay has proved all 54 lifetimes cleared. Tags cannot alias public.
        scratch = {('owned', r) for r in range(word['owned_fields'])}
        need(not scratch.intersection(assigned.values()), 'No owned/public alias')
        calls += 1
    need(calls == 18 and len(whole_helpers) == 18 * len(helper_roles), 'Fresh helpers at every native call')
    return dict(native_calls=calls, native_public=word['public'],
                native_helpers=len(helper_roles), complete_main_fields=104 * caller['roles'],
                complete_helper_fields=len(whole_helpers),
                complete_public_fields=104 * caller['roles'] + len(whole_helpers),
                reusable_owned_slots=word['owned_fields'])


def rejected(action, label):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('Mutation accepted: ' + label)


def compatible_caller(word, original, ledger, expected, targets, paid):
    """Source-bound block equality permits the same native under either caller."""
    directory = HERE / 'retained/caller-blocks'
    compressed = read(directory / 'data/caller-after.json')
    need(read(directory / 'data/caller-before.json') == original,
         'Compressed caller has the exact original source')
    checker = load(directory / 'check.py', 'retained_caller_blocks')
    checker.main()
    need(checker.equivalent(original, compressed) == (38, 60800),
         'Every changed block has the identical complete 40-field matrix')
    need(caller_invoice(word, compressed) == (targets, paid),
         'Caller compression preserves the full recursive invoice')
    budget = ordinary_bound(word, compressed, ledger)
    budget['extra_normalizer_debit'] = 12896000
    budget['raw_with_normalizer_debit'] = budget['raw_reviewed_upper'] + 12896000
    need(budget == expected['compatible_caller']['ordinary'],
         'Exact composed ordinary budget including every normalizer')
    need(budget['raw_with_normalizer_debit'] == 814811984,
         'Final native and compressed caller fit the complete envelope')
    return budget


def controls(source, word, witnesses, caller, targets, paid):
    out = {}
    first = deepcopy(witnesses[0]['witness'])
    key = next(iter(first['a']))
    first['a'][key] = str(Q(first['a'][key]) + 1)
    out['wrong_cut_functional'] = rejected(lambda: construct(source, first), 'wrong cut functional')
    wrong_main = deepcopy(word)
    second_x = wrong_main['hosted']['X2'][0]
    wrong_main['final'][second_x] = wrong_main['initial'][second_x]
    out['changed_second_main_frame'] = rejected(lambda: source_contract(wrong_main, source), 'second-main chart')
    wrong_coefficient = deepcopy(word)
    # An explicit new scalar operation from the first boundary basis block.
    i = next(i for i, e in enumerate(wrong_coefficient['program']) if e[0] == 'ADD')
    wrong_coefficient['program'][i][3] = str(2 * Q(wrong_coefficient['program'][i][3]))
    out['new_basis_coefficient'] = rejected(lambda: replay(wrong_coefficient, source), 'new basis coefficient')
    missing_move = deepcopy(word)
    del missing_move['program'][next(i for i, e in enumerate(missing_move['program']) if e[0] == 'MOVE')]
    out['missing_paid_move'] = rejected(lambda: replay(missing_move, source), 'removed MOVE')
    missing_clear = deepcopy(word)
    del missing_clear['program'][max(i for i, e in enumerate(missing_clear['program']) if e[0] == 'CLEAR')]
    out['missing_owned_clear'] = rejected(lambda: replay(missing_clear, source), 'removed owned CLEAR')
    alias = deepcopy(word)
    successor = source['public']
    private = word['public']
    for event in alias['program']:
        if event[1] == successor:
            event[1] = private
        if event[0] in ('ADD', 'COPY') and event[2] == successor:
            event[2] = private
    out['fresh_public_aliased_to_owned'] = rejected(lambda: replay(alias, source), 'fresh public/owned alias')
    bad_caller = deepcopy(caller)
    event = next(e for e in bad_caller['events'] if e[0] == 'HOST2')
    event[4] = event[2]
    out['caller_second_main_alias'] = rejected(lambda: allocation(word, bad_caller), 'caller main alias')
    underpaid = Counter(paid)
    underpaid[1] -= 1
    out['omitted_paid_job'] = rejected(lambda: need(caller_invoice(word, caller) == (targets, underpaid),
                                                 'Complete paid invoice'), 'omitted invoice job')
    return out


def run(only_controls=False):
    input_count = pins()
    source = read(HERE / 'retained/data/word.json.gz')
    caller = read(HERE / 'retained/data/caller.json')
    root = read(HERE / 'retained/data/root.json')
    expected = read(HERE / 'RESULT.json')
    witnesses = read(HERE / 'WITNESSES.json')
    committed = read(HERE / 'WORD.json.gz')
    if only_controls:
        targets, paid = caller_invoice(committed, caller)
        result = controls(source, committed, witnesses, caller, targets, paid)
        print(json.dumps(result, sort_keys=True))
        print('PASS_HELPER_SPLIT_NEGATIVE_CONTROLS')
        return
    regenerated, ledgers = regenerate(witnesses)
    need(regenerated == committed and digest(committed) == expected['word_payload_sha256'],
         'All proof-relevant output fields regenerate exactly')
    ledger = ledgers[-1]
    need(json.loads(json.dumps(ledger)) == expected['native'], 'Frozen final native ledger')
    root_checker = load(HERE / 'retained/root_check.py', 'split_root_checker')
    need(not root_checker.run(root), 'Exact unchanged two-chain root identities')
    bad_root = deepcopy(root)
    bad_root['X'][0][0] = str(Q(bad_root['X'][0][0]) + 1)
    need(bool(root_checker.run(bad_root)), 'Wrong-root-entry control is rejected')
    targets, paid = caller_invoice(committed, caller)
    need((targets, paid) == root_invoice(committed, root), 'Caller and root independently recount the invoice')
    old_targets, old_paid = caller_invoice(source, caller)
    inherited = read(HERE / 'retained/data/invoice_check.json')
    need(old_targets == Counter({int(k): v for k, v in inherited['T'].items()})
         and old_paid == Counter({int(k): v for k, v in inherited['P'].items()}),
         'The original #6902 invoice is reproduced before taking a difference')
    delta = Counter()
    for entry in witnesses:
        a, b = entry['witness']['ranks']
        delta[a] += 18
        delta[b] += 18
        delta[a + b] -= 18
    actual_delta = Counter(targets)
    actual_delta.subtract(old_targets)
    need(+actual_delta == +delta and +(-actual_delta) == +(-delta) and paid == old_paid,
         'Complete signed invoice gain: all 18 copies and unchanged paid jobs')
    need({str(k): v for k, v in sorted(targets.items())} == expected['T']
         and {str(k): v for k, v in sorted(paid.items())} == expected['P'],
         'Frozen complete invoice')
    rank_surplus = sum(r * (targets[r] - paid[r]) for r in set(targets) | set(paid))
    need(rank_surplus == 1520, 'Rank mass is preserved; the gain comes from the moment')
    allocation_ledger = allocation(committed, caller)
    need(allocation_ledger['complete_public_fields'] == sum(targets.values()),
         'Every whole productive field has exactly one target credit')
    ordinary = ordinary_bound(committed, caller, ledger)
    debit = expected.get('extra_normalizer_debit', 0)
    normalizer = read(HERE / 'retained/normalizer/RESULT.json')['primary']['accounting']
    need(debit == normalizer['extra_translation_charge']
         == sum(e[0] == 'LAMBDA' for e in caller['events']) * len(committed['ports']) * 1000,
         'Full source-bound simultaneous LAMBDA debit')
    need(normalizer['new_owned_slots'] == 0 and ledger['peak_owned_fields']
         == normalizer['new_owned_peak'] == normalizer['native_owned_peak'],
         'Normalizer bank reuse preserves the checked native scratch capacity')
    ordinary['extra_normalizer_debit'] = debit
    ordinary['raw_with_normalizer_debit'] = ordinary['raw_reviewed_upper'] + debit
    need(ordinary['raw_with_normalizer_debit'] < 10 ** 9,
         'Complete ordinary budget including explicit normalizer debit')
    need(ordinary == expected['ordinary'], 'Frozen full ordinary accounting')
    compressed_budget = compatible_caller(committed, caller, ledger, expected, targets, paid)
    host_stages = {event[1] for event in caller['events'] if event[0] == 'HOST2'}
    need(host_stages == set(range(1, len(root['stages']) + 1))
         and expected['claim']['physical_ambient_cap'] == 9 + 8 * len(root['stages']),
         'Ambient geometry derives from nine native axes and eight fresh axes per actual stage')
    compiler = compiler_dependency(expected['claim'])
    price = verify_price(targets, paid, expected['claim'])
    mutations = controls(source, committed, witnesses, caller, targets, paid)
    print(json.dumps(dict(steps=len(witnesses), pinned_inputs=input_count,
                          native=ledger, allocation=allocation_ledger, ordinary=ordinary,
                          compressed_caller_ordinary=compressed_budget,
                          compiler_dependency=compiler, price=price,
                          controls=mutations), sort_keys=True))
    print('PASS_P104_SHARED_NATIVE_HELPER_SPLITS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    run(args.controls_only)
