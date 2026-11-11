"""Directed one-helper entrance price and optimistic whole inventory bound."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
UPPER = Fraction('0.0036462214364462343366888845568981')
PINS = {
    'admission/ADMITTED.json': '41b8a189dffeb768e5843446cdc469f9cc2f0aa038d0a593cf2be43aa009a9a3',
    'inputs/7113/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/7298/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7314/EARLY-RESULT.json': 'b5043855411432b24336ecc443cba9ebfae6392e2045ddd01c87cfe2c51f5f08',
    'inputs/7314/NATIVE-RESULT.json': '336f463da5afe5b60bfd3b9f0ce8aeea5a5feb1f854613bf4218ba0b28b3371b',
    'inputs/7314/PRICE-ONLY.json': 'b757665a3a50324b2ae6649cc89f5b8d9a752c7af996f1ee894a0de47ade94e1',
    'inputs/7314/WORD.json.gz': 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
}


def unique(items):
    record = dict(items)
    if len(record) != len(items):
        raise ValueError('Duplicate JSON key')
    return record


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def authenticate(root):
    contents = {}
    for path, expected in PINS.items():
        raw = (root / path).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f'Changed input {path}')
        contents[path] = raw
    admission = read(contents['admission/ADMITTED.json'])
    assert admission['head'] == HEAD and admission['status'] == 'independently_reproduced_comparable'
    assert admission['caller_sha256'] == PINS['inputs/7113/CALLER.json']
    assert set(admission['stages']) == {'early', 'native', 'caller', 'frontier'}
    for receipt in [*admission['stages'].values(), admission['source_history']['evidence']]:
        assert sha256((root / 'admission' / receipt['path']).read_bytes()).hexdigest() == receipt['sha256']
    return contents


def histogram(value):
    return Counter({int(rank): n for rank, n in value.items()})


def interval(value):
    return list(map(str, value))


def quote(root):
    inputs = authenticate(root)
    invoice = read(inputs['inputs/7314/EARLY-RESULT.json'])['invoice']
    paid, targets = (histogram(invoice[key]) for key in ('P', 'T'))
    helpers = histogram(read(inputs['inputs/7314/NATIVE-RESULT.json'])['native']['helpers'])
    assert helpers == {1:18, 2:21, 3:47, 4:225, 5:80, 6:43, 7:19, 8:32, 9:616}
    exact = read(inputs['inputs/7314/PRICE-ONLY.json'])
    assert exact['head'] == HEAD and Fraction(exact['new_crossing'][1]) == UPPER
    assert paid == histogram(exact['paid']) and targets == histogram(exact['productive'])
    net = targets.copy()
    net.subtract(paid)
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    assert sum(k*v for k,v in net.items()) == invoice['S'] == 1424
    assert invoice['empty_root_credits'] == 0
    directed = run_path(str(root / 'inputs/7298/pricing.py'))['cost']
    baseline = directed(net, UPPER)
    assert baseline[1] < 0
    rows = {}
    for t in range(2, 10):
        delta = Counter({t: -17})
        delta[t-1] += 17
        delta[1] += 17
        new = net.copy()
        new.update(delta)
        new_with_setup = new.copy()
        new_with_setup[1] -= 17
        credit = directed(delta, UPPER)
        margin = directed(new, UPPER)
        setup_margin = directed(new_with_setup, UPPER)
        assert 0 < credit[0] <= credit[1] < 17
        assert margin[0] > 0 > setup_margin[1]
        assert sum(k*v for k,v in delta.items()) == 0
        rows[t] = {
            'inventory_upper': helpers[t], 'rank': t,
            'signed_net_delta': dict(delta), 'credit': interval(credit),
            'margin': interval(margin), 'margin_with_extra_rank_one': interval(setup_margin),
        }
    gross = sum(helpers[t] * Fraction(row['credit'][1]) for t, row in rows.items())
    return {'head': HEAD, 'caller': CALLER, 'claim': '0.003646221436446', 'crossing_upper': str(UPPER),
            'input_sha256': PINS, 'old_margin': interval(baseline), 'paid': dict(paid),
            'targets': dict(targets), 'helpers': dict(helpers), 'copies': 17,
            'rank_prices': rows, 'eligible_stock_upper_before_contact': 1083,
            'whole_optimistic_upper': str(gross),
            'one_edit_optimistic_upper': max((row['credit'][1] for row in rows.values()), key=Fraction),
            'limits': {'roles': 1101, 'seconds': 20, 'contract_survivors': 1, 'contract_seconds': 120}}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    print(dumps(quote(args.root), sort_keys=True, indent=2))
