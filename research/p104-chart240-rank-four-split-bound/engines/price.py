"""Price one productive rank-four split at the admitted #7314 crossing."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps
from pathlib import Path
from runpy import run_path
from tempfile import NamedTemporaryFile

ADAPTER = 'entrance_price.py'
ADAPTER_SHA = '37cffc5f28dda64a125e5ecbd9f4c8d112296c9a21511b8d363b1c0ce362695f'
WITNESS = 'inputs/7314/WITNESS.json'
WITNESS_SHA = 'e1aa1bcf2174f4dcedbf8e94474eb24dc46c8c588fff8f2c4c5bcb489668a315'


def checked(path, expected):
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f'Changed input {path.name}')
    return data


def quote(root):
    if not __debug__:
        raise ValueError('Run with proof assertions enabled')
    adapter_path = root / ADAPTER
    checked(adapter_path, ADAPTER_SHA)
    adapter = run_path(str(adapter_path))
    inputs = adapter['authenticate'](root)
    checked(root / WITNESS, WITNESS_SHA)
    pins = {ADAPTER: ADAPTER_SHA, WITNESS: WITNESS_SHA, **adapter['PINS']}
    assert len(pins) == len(adapter['PINS']) + 2
    head, caller_head, crossing = (adapter[name] for name in ('HEAD', 'CALLER', 'UPPER'))
    read, histogram = adapter['read'], adapter['histogram']
    admission = read(inputs['admission/ADMITTED.json'])
    receipts = [*admission['stages'].values(), admission['source_history']['evidence']]
    for receipt in receipts:
        path = Path(receipt['path'])
        assert not path.is_absolute() and path.parts and '..' not in path.parts
        key = str(Path('admission') / path)
        assert key not in pins
        checked(root / key, receipt['sha256'])
        pins[key] = receipt['sha256']
    assert all(stage['exit'] == 0 for stage in admission['stages'].values())
    assert set(admission['assumptions']) == {
        'native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery',
    }
    caller = read(inputs['inputs/7113/CALLER.json'])
    calls = sum(event[0] == 'J' for event in caller['events'])
    assert calls == caller['stages'] == 17
    invoice = read(inputs['inputs/7314/EARLY-RESULT.json'])['invoice']
    paid, targets = (histogram(invoice[k]) for k in ('P', 'T'))
    reference = read(inputs['inputs/7314/PRICE-ONLY.json'])
    assert reference['head'] == head and Fraction(reference['new_crossing'][1]) == crossing
    assert paid == histogram(reference['paid']) and targets == histogram(reference['productive'])
    net = targets.copy()
    net.subtract(paid)
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    assert sum(r*n for r, n in net.items()) == invoice['S'] == 1424
    assert invoice['empty_root_credits'] == 0
    directed = run_path(str(root / 'inputs/7298/pricing.py'))['cost']
    old = directed(net, crossing)
    assert old[1] < 0
    interval = adapter['interval']
    prices = {}
    for a, b in ((1, 3), (2, 2)):
        delta = Counter({4: -calls})
        delta[a] += calls
        delta[b] += calls
        new_targets = targets.copy()
        new_targets.update(delta)
        assert all(n > 0 for n in new_targets.values())
        assert sum(new_targets.values()) == 22478
        assert sum(r*n for r, n in delta.items()) == 0
        new = net.copy()
        new.update(delta)
        extra = new.copy()
        extra[1] -= 1
        credit, margin, extra_margin = (directed(h, crossing) for h in (delta, new, extra))
        assert 0 < credit[0] <= credit[1] < Fraction(51, 125)
        assert margin[0] > 0 > extra_margin[1]
        prices[f'{a}+{b}'] = {
            'partition': [a, b], 'paid_delta': {}, 'target_delta': dict(delta),
            'targets': dict(new_targets), 'credit': interval(credit), 'margin': interval(margin),
            'margin_with_one_extra_rank_one_position': interval(extra_margin),
        }
    assert Fraction(prices['1+3']['credit'][1]) < Fraction(prices['2+2']['credit'][0])
    return {
        'head': head, 'caller': caller_head, 'claim': admission['kappa'],
        'crossing_upper': str(crossing), 'input_sha256': pins, 'copies': calls,
        'paid': dict(paid), 'targets': dict(targets), 'rank_surplus': invoice['S'],
        'empty_root_credits': invoice['empty_root_credits'], 'old_margin': interval(old),
        'split_prices': prices, 'stock_edits_cap': 1,
        'one_edit_optimistic_upper': prices['2+2']['credit'][1],
        'support_limits': {'keys': 256, 'seconds': 45, 'construction_cases': 1, 'construction_seconds': 120},
        'scope': 'Price only. One fixed-paid rank-four productive split with additional ordinary and physical costs free.',
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = dumps(quote(args.root), sort_keys=True, indent=2) + '\n'
    if args.out is None:
        print(result, end='')
        return
    with NamedTemporaryFile(mode='w', dir=args.out.parent, prefix='price-', delete=False) as output:
        output.write(result)
    Path(output.name).replace(args.out)


if __name__ == '__main__':
    main()
