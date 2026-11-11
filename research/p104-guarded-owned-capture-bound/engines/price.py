"""Reprice deletion of one paid owned capture lifetime in admitted #7314."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from tempfile import NamedTemporaryFile

PINS = {
    'round63/price.py': 'ede3c496e0295481505136aa8411035cf7c2206df3bfe61d0bf0c9c47fea731c',
    'round63/price.json': '5943e27d6dd81d2c4b8feae2d8398da3b8cd0d218fa86e89cf6523e8fb4e61e9',
    'round41/RESULT.json': '1b993aa8c66ffce5d2d9f13cafae320c62230722d599d251fa61afc6534b1bc7',
    '7314/construct.py': '2dec457c43300dbbdf4113db77b061c1e5363a76b79f49b786d95b64ab22c62b',
}
WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
OLD_HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
OLD_WORD = '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756'


def checked(path, expected):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f'Changed input {path.name}')
    return raw


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('Duplicate JSON key')
    return result


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def histogram(value):
    result = Counter({int(r): n for r, n in value.items()})
    assert len(result) == len(value)
    assert all(r > 0 and type(n) is int and n > 0 for r, n in result.items())
    return result


def interval(values):
    return list(map(str, values))


def encoded(doc):
    return (dumps(doc, indent=2, sort_keys=True) + '\n').encode()


def context(root):
    inputs = {path: checked(root / path, digest) for path, digest in PINS.items()}
    prior_root = root / 'round63/price-inputs'
    prior = run_path(str(root / 'round63/price.py'))['quote'](prior_root)
    assert encoded(prior) == inputs['round63/price.json']
    assert prior['input_sha256']['inputs/7314/WORD.json.gz'] == WORD
    pins = PINS.copy()
    for path, digest in prior['input_sha256'].items():
        key = f'round63/price-inputs/{path}'
        assert key not in pins
        pins[key] = digest
    owned = read(inputs['round41/RESULT.json'])
    assert owned['scientific_head'] == OLD_HEAD and owned['word_sha256'] == OLD_WORD
    assert owned['scope_exhausted'] and owned['paid_owned_moves'] == len(owned['records']) == 47
    stock = Counter(row['rank'] for row in owned['records'])
    assert stock == histogram(owned['paid_owned_histogram']) == {1: 20, 2: 9, 3: 2, 4: 13, 5: 2, 6: 1}
    assert len({row['literal_index'] for row in owned['records']}) == 47
    assert all(row['role'] != 1525 for row in owned['records'])
    paid, targets = (histogram(prior[key]) for key in ('paid', 'targets'))
    crossing = Fraction(prior['crossing_upper'])
    directed = run_path(str(prior_root / 'inputs/7298/pricing.py'))['cost']
    net = targets.copy()
    net.subtract(paid)
    assert sum(paid.values()) == 110536 and sum(targets.values()) == 22461
    assert sum(r*n for r, n in net.items()) == prior['rank_surplus'] == 1424
    assert interval(directed(net, crossing)) == prior['old_margin'] and prior['copies'] == 17
    return prior, pins, stock, paid, targets, net, crossing, directed


def removal_price(removed, paid, net, crossing, directed):
    deleted = Counter({r: 17*n for r, n in removed.items()})
    candidate_paid = paid - deleted
    assert sum(candidate_paid.values()) == 110536 - sum(deleted.values())
    after = net.copy()
    after.update(deleted)
    credit, margin = (directed(values, crossing) for values in (deleted, after))
    rank_surplus = 1424 + sum(r*n for r, n in deleted.items())
    assert sum(r*n for r, n in after.items()) == rank_surplus
    assert credit[0] >= 17 and margin[0] > 0
    return {
        'removed_owned_moves_per_copy': dict(removed),
        'paid_delta': {r: -n for r, n in deleted.items()}, 'target_delta': {},
        'paid': dict(candidate_paid), 'paid_positions': sum(candidate_paid.values()),
        'productive_fields': 22461, 'rank_surplus': rank_surplus,
        'credit': interval(credit), 'complete_margin': interval(margin),
    }


def quote_stock(ctx):
    prior, pins, stock, paid, targets, net, crossing, directed = ctx
    relaxation = removal_price(stock, paid, net, crossing, directed)
    return {
        'head': prior['head'], 'caller': prior['caller'], 'word_sha256': WORD,
        'claim': prior['claim'], 'crossing_upper': str(crossing), 'copies': 17,
        'input_sha256': pins, 'old_margin': prior['old_margin'],
        'paid': dict(paid), 'targets': dict(targets),
        'paid_positions': 110536, 'productive_fields': 22461, 'rank_surplus': 1424,
        'empty_root_credits': 0, 'paid_owned_histogram': dict(stock), 'paid_owned_moves': sum(stock.values()),
        'copy_capture_paid_lifetimes': 0, 'owned_lifetimes': 72, 'stock_edits_cap': 1,
        'whole_stock_relaxation': relaxation,
        'one_edit_optimistic_upper_before_structure': relaxation['credit'][1],
        'per_rank': {r: removal_price({r: 1}, paid, net, crossing, directed) for r in stock},
        'scope': 'Price before structure. All 47 paid owned MOVEs are credited once in the relaxation; actual scope is one lifetime.',
    }


def quote_sites(ctx, inventory, inventory_sha, stock_price, stock_sha):
    prior, _, stock, paid, _, net, crossing, directed = ctx
    assert inventory['head'] == prior['head'] and inventory['word_sha256'] == WORD
    assert inventory['price_sha256'] == stock_sha and type(inventory['complete']) is bool
    survivors = inventory['survivors']
    assert len(survivors) <= stock_price['owned_lifetimes']
    seen_lifetimes, seen_moves, counted = set(), set(), Counter()
    prices = []
    for case in survivors:
        role, init, capture, clear = (case[k] for k in ('role', 'init', 'capture', 'clear'))
        assert 1501 <= role < 1569 and 0 <= init < capture < clear < 76461
        key = role, init, clear
        assert key not in seen_lifetimes
        seen_lifetimes.add(key)
        counts = Counter()
        for move in case['moves']:
            clock, rank = move['clock'], move['rank']
            assert type(rank) is int and capture < clock < clear and clock not in seen_moves
            seen_moves.add(clock)
            counts[rank] += 1
        assert counts and counts <= stock
        counted.update(counts)
        prices.append({'key': list(key), 'capture': capture, 'price': removal_price(counts, paid, net, crossing, directed)})
    assert counted <= stock
    if inventory['complete']:
        unvisited_upper = Fraction(0)
    else:
        unvisited_upper = Fraction(stock_price['one_edit_optimistic_upper_before_structure'])
    visited_upper = max((Fraction(row['price']['credit'][1]) for row in prices), default=Fraction(0))
    return {
        'head': prior['head'], 'word_sha256': WORD, 'price_sha256': stock_sha,
        'inventory_sha256': inventory_sha, 'structure_complete': inventory['complete'],
        'priced_survivors': len(prices), 'prices': prices,
        'visited_best_single_lifetime_upper': str(visited_upper),
        'unvisited_single_lifetime_upper': str(unvisited_upper),
        'one_edit_optimistic_upper': str(max(visited_upper, unvisited_upper)),
        'scope': 'Directed prices for structurally eligible lifetimes, before arbitrary-input donor checks and additional charges.',
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--stock', type=Path)
    parser.add_argument('--stock-sha')
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--inventory-sha')
    args = parser.parse_args()
    if not __debug__:
        parser.error('Run with proof assertions enabled')
    ctx = context(args.root)
    result = quote_stock(ctx)
    if any((args.stock, args.stock_sha, args.inventory, args.inventory_sha)):
        if not all((args.stock, args.stock_sha, args.inventory, args.inventory_sha)):
            parser.error('Specify both stock and inventory with their exact SHA-256 pins')
        assert checked(args.stock, args.stock_sha) == encoded(result)
        inventory = read(checked(args.inventory, args.inventory_sha))
        result = quote_sites(ctx, inventory, args.inventory_sha, result, args.stock_sha)
    raw = encoded(result)
    if args.out is None:
        print(raw.decode(), end='')
        return
    with NamedTemporaryFile(mode='wb', dir=args.out.parent, prefix='price-', delete=False) as output:
        output.write(raw)
    written = Path(output.name)
    written.chmod(0o644)
    written.replace(args.out)


if __name__ == '__main__':
    main()
