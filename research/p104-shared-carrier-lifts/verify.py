"""Rebuild the shared-carrier lift word from the PR6372 word and check the complete bound.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
The source, native, price and compiler engines retain the credits in NOTICE.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
STATUS = 'PASS_P104_SHARED_CARRIER_LIFTS_KAPPA_00315120'
ANCHORS = (520, 655, 544, 671, 472, 624)
CARRIERS = (171, 208, 130)


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def delta(after, before):
    out = Counter(after)
    out.subtract(before)
    return {rank: count for rank, count in out.items() if count}


def run(build_only):
    from support import (ROOT, TREE, SOURCE_WORD, authenticate, checkers,
                         inputs, load, need, read)
    raw = inputs()
    from construct import construct

    source = json.loads(gzip.decompress(raw[SOURCE_WORD]))
    word = construct(source, read(HERE / 'LIFTS.json'))
    need(read(HERE / 'WORD.json.gz') == word, 'Every regenerated word field')
    need(all(word[k] == value for k, value in source.items()
             if k not in ('program', 'initial')), 'Unchanged frames, finals and interface')
    need({r for r in range(770) if word['initial'][r] != source['initial'][r]} == set(ANCHORS)
         and word['initial'][520] == 106 and word['initial'][472] == 105,
         'Exactly six anchors start at their entrance frames')
    need(word['final'] == source['final'], 'Unchanged helper outputs')
    need(all(type(e[4]) is bool for e in word['program'] if e[0] == 'MOVE'),
         'Boolean ownership flags')
    text = raw[TREE + 'pricing.py'].decode()
    for before, after in read(HERE / 'PRICING-EDITS.json'):
        need(text.count(before) == 1, 'One occurrence of each declared price edit')
        text = text.replace(before, after)
    need(text == (HERE / 'pricing.py').read_text(), 'Exact declared price adapter')
    controller = load(ROOT / TREE / 'controller.py', 'controller')
    physical_module = load(ROOT / TREE / 'physical.py', 'contact_physical')
    module_check = load(ROOT / TREE / 'module_check.py', 'contact_module')
    price_module = load(HERE / 'pricing.py', 'contact_price')
    caller = controller.construct()
    need(encode(caller) == read(ROOT / TREE / 'CONTROLLER.json'),
         'Unchanged fixed caller payload')
    module = module_check.run()
    caller_result = controller.replay(caller)
    controls = controller.controls(caller)
    with checkers() as (L, root):
        baseline, local = L.replay(source), L.replay(word)
        paid_delta = delta(local['paid'], baseline['paid'])
        target_delta = delta(local['helpers'], baseline['helpers'])
        need(paid_delta == {1: 6, 3: -3, 4: 3, 5: -3}, 'Exact paid change')
        need(target_delta == {8: 6, 9: -6}, 'Exact productive debit')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                     'peak_owned_fields', 'real_scalar_allowance', 'paid_rank_mass'))
             == (770, 29, 43, 13, 129670, 5926), 'Exact local inventory')
        need(local['owned_lifetimes'] == baseline['owned_lifetimes'] == 43
             and local['owned_fields'] == baseline['owned_fields'],
             'No owned lifetime or field is added')
        P = word['program']
        base_events = {json.dumps(e) for e in source['program']}
        new = [i for i, e in enumerate(P) if json.dumps(e) not in base_events]
        adds = [i for i in new if P[i][0] == 'ADD']
        moves = [i for i in new if P[i][0] == 'MOVE']
        restores = [i for i in new if P[i][0] == 'ADD' and P[i][-1] == 127]
        lift_adds = [i for i in adds if P[i][-1] != 127]
        need(restores and lift_adds and moves, 'Lift events present')

        def drop(i):
            bad = deepcopy(word)
            del bad['program'][i]
            return bad

        def change(i, k, value):
            bad = deepcopy(word)
            bad['program'][i][k] = value
            return bad

        mid = lift_adds[len(lift_adds) // 2]
        probes = {
            'lift_response_doubled': change(mid, 3, str(2 * Q(P[mid][3]))),
            'lift_response_sign_flipped': change(lift_adds[0], 3, str(-Q(P[lift_adds[0]][3]))),
            'restore_event_dropped': drop(restores[-1]),
            'first_restore_event_dropped': drop(restores[0]),
            'first_delivery_event_dropped': drop(lift_adds[0]),
            'anchor_event_dropped': drop(moves[0]),
            'last_move_dropped': drop(moves[-1]),
            'move_destination_shifted': change(moves[1], 3, P[moves[1]][3] + 1
                                               if P[moves[1]][3] + 1 < len(word['frames']) else P[moves[1]][3] - 1),
        }
        for label, bad in probes.items():
            controls['lift_' + label] = reject(lambda bad=bad: L.replay(bad))
        bad = deepcopy(word)
        bad['initial'][ANCHORS[0]] = source['initial'][ANCHORS[0]]
        controls['lift_anchor_entrance_reverted'] = reject(lambda: L.replay(bad))
        print('PASS source pin, rebuilt word, local deltas and lift controls', flush=True)
        if build_only:
            return None
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401,
             'Every separate dense column')
        native = L.native(word)
        physical = physical_module.physical(caller, word, L)
        print('PASS separate columns, native phases and all caller contacts', flush=True)
        price = price_module.run(local, native, caller, physical, L)
        need(price['raw_root_interval'] ==
             ['315120852329/100000000000000', '31512085233/10000000000000'],
             'Exact new rational crossing')
        old_targets, old_paid = controller.formula_invoice(baseline)
        need(delta({int(r): n for r, n in price['paid'].items()}, old_paid) ==
             {r: 19*n for r, n in paid_delta.items()}, 'Paid change at all nineteen calls')
        need(delta({int(r): n for r, n in price['targets'].items()}, old_targets) ==
             {r: 19*n for r, n in target_delta.items()}, 'Target debit at all nineteen calls')
        E = load(root / 'research/higher-moment-strictification/verify.py', 'contact_comparison')

        def old_margin(k):
            target, paid = E.moment(old_targets, 1-k), E.moment(old_paid, 1-k)
            return target[0]-paid[1], target[1]-paid[0]

        old_upper = old_margin(price_module.KAPPA)[1]
        need(old_upper < 0, 'The PR6372 word with this same caller fails the new claim')
        old_root = [Q('0.00315087900390'), Q('0.00315087900391')]
        need(old_margin(old_root[0])[0] > 0 and old_margin(old_root[1])[1] < 0,
             'Exact same-caller PR6372 crossing')
        bad = deepcopy(local)
        bad['paid'][4] -= 1
        controls['unpaid_native_move'] = reject(
            lambda: price_module.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        bad['helpers'][8] -= 1
        controls['missing_productive_debit'] = reject(
            lambda: price_module.assemble(bad, native, caller, physical))
        for pin in read(HERE / 'SOURCES.json')['files']:
            if pin['path'] in raw:
                data = raw[pin['path']]
                controls['damaged_' + pin.get('origin_path', pin['path'])] = reject(
                    lambda data=data, pin=pin: authenticate(bytes([data[0] ^ 1]) + data[1:], pin))
        print('PASS complete price, both interval engines, compiler, outer bounds and controls', flush=True)
        return encode(dict(
            status=STATUS, base_commit=read(HERE / 'SOURCES.json')['base_commit'],
            source_head='b556600ffe14be72406b03a47c661f3c7f1aff06',
            events=len(word['program']), source_local=baseline, local=local,
            paid_delta=paid_delta, target_delta=target_delta,
            tariff_scope='Positive at power exponents of about 0.873 to 1 only; zero at linear cost.',
            separate_columns=columns, native=native, module=module,
            caller=caller_result, physical=physical, complete_cost=price,
            same_caller_source_margin_upper=old_upper, same_caller_source_root=old_root,
            controls=controls,
            assumptions=['native_all_columns', 'owned_erasure', 'compiler',
                         'precision_tape', 'analytic_recovery'],
            limits=['The uniform word and rounded multiplier are not materialized.',
                    'Author checks do not establish independent scientific acceptance.',
                    'The gain is small, source-bound and tied to the stated power exponent; it is zero at linear cost and not positive for every concave tariff.',
                    'The selected frontier is unchanged.']))


def main():
    with tempfile.TemporaryDirectory(prefix='shared-carrier-cache-') as cache:
        sys.pycache_prefix = cache
        sys.path.insert(0, str(HERE))
        from support import need, read
        result = run('--build-only' in sys.argv)
    if result is not None:
        if '--write' in sys.argv:
            (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        else:
            need(read(HERE / 'RESULT.json') == result, 'Exact complete result')
    print(STATUS + ('_BUILD' if result is None else ''), flush=True)


if __name__ == '__main__':
    main()
