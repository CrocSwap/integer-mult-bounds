"""Check the construction, native maps, fixed caller and complete price.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The unchanged proof engines retain the credits in NOTICE.
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
STATUS = 'PASS_P104_JOINT_OUTPUT_CONTRACTION_KAPPA_00315057'


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


def word_controls(L, word, witness):
    controls = {}
    for label, index in witness['control_indices'].items():
        bad = deepcopy(word)
        del bad['program'][index]
        controls['missing_' + label] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['final'][703] = 127
    controls['missing_output_target_debit'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['frames'][1094] = [1, 2, 4, 8, 16]
    controls['wrong_output_subspace'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    index = next(i for i, e in enumerate(bad['program']) if e == ['INIT', 770, 127])
    bad['program'][index][2] = 3
    controls['wrong_temporary_frame'] = reject(lambda: L.replay(bad))
    return controls


def run(build_only):
    from construct import construct, encode, payload
    from support import ROOT, TREE, WORD, authenticate, checkers, inputs, load, need, read

    raw = inputs()
    source = json.loads(gzip.decompress(raw[WORD]))
    word, witness = construct(source)
    need(gzip.decompress((HERE / 'WORD.json.gz').read_bytes()) == payload(word),
         'Every regenerated word payload byte')
    need(read(HERE / 'BASIS.json') == encode(witness), 'Every regenerated basis witness')
    need(len(word['program']) == 17657 and len(word['frames']) == 1095, 'Exact event and frame counts')
    need(all(type(e[4]) is bool for e in word['program'] if e[0] == 'MOVE'), 'Boolean ownership flags')
    need(all(word[k] == v for k, v in source.items() if k not in ('program', 'frames', 'final')),
         'All source inputs and other interface fields unchanged')
    expected_finals = {703: 1094, 393: 246, 707: 246, 484: 246, 297: 246,
                       485: 246, 226: 246, 361: 245, 451: 245}
    need({r: word['final'][r] for r in range(770) if word['final'][r] != source['final'][r]} == expected_finals,
         'Exactly nine changed output frames')
    need(word['frames'][:1094] == source['frames'] and word['frames'][1094] == [7, 9, 35, 66, 400],
         'Every original frame byte and the new output frame')
    text = raw[TREE + 'pricing.py'].decode()
    for before, after in read(HERE / 'PRICING-EDITS.json'):
        need(text.count(before) == 1, 'One occurrence of each declared price edit')
        text = text.replace(before, after)
    need(text == (HERE / 'pricing.py').read_text(), 'Exact declared price adapter')
    controller = load(ROOT / TREE / 'controller.py', 'controller')
    physical_module = load(ROOT / TREE / 'physical.py', 'joint_physical')
    module_check = load(ROOT / TREE / 'module_check.py', 'joint_module')
    price_module = load(HERE / 'pricing.py', 'joint_price')
    caller = controller.construct()
    need(encode(caller) == read(ROOT / TREE / 'CONTROLLER.json'), 'Unchanged fixed caller payload')
    module = module_check.run()
    caller_result = controller.replay(caller)
    controls = controller.controls(caller)
    with checkers() as (L, root):
        baseline, local = L.replay(source), L.replay(word)
        paid_delta = delta(local['paid'], baseline['paid'])
        target_delta = delta(local['helpers'], baseline['helpers'])
        need(paid_delta == {1: 14, 2: -4, 3: -3, 4: 4, 5: -5}, 'Exact local paid change')
        need(target_delta == {5: 1, 8: 8, 9: -9}, 'Exact local productive target debit')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                     'peak_owned_fields', 'real_scalar_allowance', 'paid_rank_mass')) ==
             (770, 29, 41, 13, 128694, 5934), 'Exact local inventory')
        controls.update(word_controls(L, word, witness))
        print('PASS exact source, joint bases, zero temporary rows, all scalar inputs and controls', flush=True)
        if build_only:
            return None
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401, 'Every separate dense column')
        native = L.native(word)
        physical = physical_module.physical(caller, word, L)
        print('PASS separate columns, native absolute phases and all fixed caller contacts', flush=True)
        price = price_module.run(local, native, caller, physical, L)
        need(price['raw_root_interval'] ==
             ['19691137593/6250000000000', '315058201489/100000000000000'], 'Exact new rational crossing')
        old_targets, old_paid = controller.formula_invoice(baseline)
        need(delta({int(r): n for r, n in price['paid'].items()}, old_paid) ==
             {r: 19 * n for r, n in paid_delta.items()}, 'Complete paid change at all nineteen calls')
        need(delta({int(r): n for r, n in price['targets'].items()}, old_targets) ==
             {r: 19 * n for r, n in target_delta.items()}, 'Complete target debit at all nineteen calls')
        E = load(root / 'research/higher-moment-strictification/verify.py', 'joint_source_comparison')

        def old_margin(k):
            target, paid = E.moment(old_targets, 1 - k), E.moment(old_paid, 1 - k)
            return target[0] - paid[1], target[1] - paid[0]

        old_upper = old_margin(price_module.KAPPA)[1]
        need(old_upper < 0, 'The old supplier with this same caller fails the new claim')
        old_root = [Q('0.00314981300605'), Q('0.00314981300606')]
        need(old_margin(old_root[0])[0] > 0 and old_margin(old_root[1])[1] < 0,
             'Exact same-caller source crossing, as published in PR6350')
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_native_move'] = reject(lambda: price_module.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        bad['helpers'][8] -= 1
        controls['missing_productive_debit'] = reject(lambda: price_module.assemble(bad, native, caller, physical))
        for pin in read(HERE / 'SOURCES.json')['files']:
            if pin['usage'] == 'input':
                data = raw[pin['path']]
                controls['damaged_' + pin['path']] = reject(
                    lambda data=data, pin=pin: authenticate(bytes([data[0] ^ 1]) + data[1:], pin))
        print('PASS complete signed invoice, two interval engines, compiler, outer checks and controls', flush=True)
        return encode(dict(
            status=STATUS, base_commit=read(HERE / 'SOURCES.json')['base_commit'],
            events=len(word['program']), source_local=baseline, local=local,
            paid_delta=paid_delta, target_delta=target_delta, separate_columns=columns, native=native,
            module=module, caller=caller_result, physical=physical, complete_cost=price,
            same_caller_source_margin_upper=old_upper, same_caller_source_root=old_root, controls=controls,
            assumptions=['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery'],
            limits=['The uniform word and rounded multiplier are not materialized.',
                    'Author checks do not establish independent scientific acceptance.',
                    'The gain is small. The donor breakthrough target is not met.',
                    'The selected frontier is unchanged.']))


def main():
    with tempfile.TemporaryDirectory(prefix='joint-output-cache-') as cache:
        sys.pycache_prefix = cache
        sys.path.insert(0, str(HERE))
        from support import need, read
        result = run('--build-only' in sys.argv)
    if result is not None:
        if '--write' in sys.argv:
            (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        else:
            need(read(HERE / 'RESULT.json') == result, 'Exact retained complete result')
    print(STATUS + ('_BUILD' if result is None else ''), flush=True)


if __name__ == '__main__':
    main()
