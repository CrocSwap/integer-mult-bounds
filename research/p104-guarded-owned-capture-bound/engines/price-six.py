"""Price the six descending-read cases from sealed inventory only."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

STOCK_SHA = 'e7808a744ff1707113c88636c0369411329088969092b3aece956bfa64ea7ca6'
INVENTORY_SHA = '3688c37f833027f808a8bb3c8e7c2a1645b804e3786969b2c003609dc95988e9'


def read(path, digest):
    raw = Path(path).read_bytes()
    assert sha256(raw).hexdigest() == digest
    return loads(raw)


def main():
    stock = read('price-stock.json', STOCK_SHA)
    inventory = read('price-inputs/INVENTORY.json', INVENTORY_SHA)
    assert inventory['complete'] and inventory['price_sha256'] == STOCK_SHA
    assert inventory['head'] == stock['head'] and inventory['word_sha256'] == stock['word_sha256']
    cases = []
    for row in inventory['decisions']:
        if row['decision'] != 'read chart does not have higher rank':
            continue
        move, = row['moves']
        first = row['reads'][0]
        assert move['clock'] + 1 == first['clock'] and move['new'] == first['chart']
        price = stock['per_rank'][str(move['rank'])]
        cases.append({'role': row['role'], 'move': move, 'first_read': first,
                      'price': price})
    assert len(cases) == len({row['role'] for row in cases}) == 6
    assert Counter(row['move']['rank'] for row in cases) == {1: 3, 2: 3}
    ceiling = max(Fraction(row['price']['credit'][1]) for row in cases)
    result = {'head': stock['head'], 'word_sha256': stock['word_sha256'],
              'stock_price_sha256': STOCK_SHA, 'inventory_sha256': INVENTORY_SHA,
              'cases': cases, 'lifetime_cap': 1, 'one_edit_optimistic_upper': str(ceiling),
              'scope': 'Price-only for six descending first reads with one paid MOVE each.'}
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run with proof assertions enabled')
    main()
