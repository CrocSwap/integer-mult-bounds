"""Check both helper contractions and the complete fixed caller bound.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
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
STATUS = 'PASS_P104_CONTACT_BLOCK_CONTRACTION_KAPPA_00315087'


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
    from support import (ROOT, TREE, SOURCE_WORD, SOURCE_BASIS, authenticate, checkers,
                         inputs, load, need, read)
    raw = inputs()
    legacy = load(ROOT / SOURCE_BASIS, 'legacy_basis')
    from construct import construct

    source = json.loads(gzip.decompress(raw[SOURCE_WORD]))
    word, witness = construct(source)
    need(read(HERE / 'WORD.json.gz') == word, 'Every regenerated word field')
    need(read(HERE / 'BASIS.json') == legacy.encode(witness), 'Every basis witness field')
    need(all(word[k] == value for k, value in source.items()
             if k not in ('program', 'final')), 'Unchanged inputs, frames and source interface')
    need({r: word['final'][r] for r in range(770)
          if word['final'][r] != source['final'][r]} == {224: 245, 227: 245},
         'Exactly two changed helper outputs')
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
    need(legacy.encode(caller) == read(ROOT / TREE / 'CONTROLLER.json'),
         'Unchanged fixed caller payload')
    module = module_check.run()
    caller_result = controller.replay(caller)
    controls = controller.controls(caller)
    with checkers() as (L, root):
        baseline, local = L.replay(source), L.replay(word)
        paid_delta = delta(local['paid'], baseline['paid'])
        target_delta = delta(local['helpers'], baseline['helpers'])
        need(paid_delta == {4: 2, 5: -2}, 'Exact paid change')
        need(target_delta == {8: 2, 9: -2}, 'Exact productive debit')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                     'peak_owned_fields', 'real_scalar_allowance', 'paid_rank_mass'))
             == (770, 29, 43, 13, 129618, 5932), 'Exact local inventory')
        need(local['owned_lifetimes'] == baseline['owned_lifetimes'] + 2,
             'Both new owned lifetimes are counted')
        for label, index in witness['control_indices'].items():
            bad = deepcopy(word)
            del bad['program'][index]
            controls['missing_' + label] = reject(lambda: L.replay(bad))
        for r in (224, 227):
            bad = deepcopy(word)
            bad['final'][r] = source['final'][r]
            controls['missing_target_debit_' + str(r)] = reject(lambda: L.replay(bad))
        print('PASS source pins, exact bases, zero rows, arbitrary inputs and controls', flush=True)
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
             ['31508790039/10000000000000', '315087900391/100000000000000'],
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
        need(old_upper < 0, 'The source with this same caller fails the new claim')
        old_root = [Q('0.00315058201488'), Q('0.00315058201489')]
        need(old_margin(old_root[0])[0] > 0 and old_margin(old_root[1])[1] < 0,
             'Exact same-caller source crossing')
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
        return legacy.encode(dict(
            status=STATUS, base_commit=read(HERE / 'SOURCES.json')['base_commit'],
            source_head='db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3',
            events=len(word['program']), source_local=baseline, local=local,
            paid_delta=paid_delta, target_delta=target_delta,
            separate_columns=columns, native=native, module=module,
            caller=caller_result, physical=physical, complete_cost=price,
            same_caller_source_margin_upper=old_upper, same_caller_source_root=old_root,
            controls=controls,
            assumptions=['native_all_columns', 'owned_erasure', 'compiler',
                         'precision_tape', 'analytic_recovery'],
            limits=['The uniform word and rounded multiplier are not materialized.',
                    'Author checks do not establish independent scientific acceptance.',
                    'The gain is small and source-bound.',
                    'The selected frontier is unchanged.']))


def main():
    with tempfile.TemporaryDirectory(prefix='contact-block-cache-') as cache:
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
