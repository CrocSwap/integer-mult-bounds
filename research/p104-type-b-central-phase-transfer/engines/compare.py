"""Compare exact and modular Type B central-phase dispositions by pair."""

from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('price', type=Path)
    parser.add_argument('body_one', type=Path)
    parser.add_argument('exact', type=Path)
    args = parser.parse_args()
    price, body, exact = [loads(path.read_bytes()) for path in (args.price, args.body_one, args.exact)]
    assert body['price_sha256'] == sha256(args.price.read_bytes()).hexdigest()
    assert not body['unvisited'] and not exact['unvisited']
    expected = {tuple(key[:2]) for key in price['pair_keys']}
    modular = {tuple(row['key'][:2]): row for row in body['records']}
    rational = {(row['odd'], row['even']): row for row in exact['records']}
    assert set(modular) == set(rational) == expected
    assert len(expected) == len(body['records']) == len(exact['records']) == 104
    for key, row in modular.items():
        verdict = rational[key]
        witness = row['witness']
        assert verdict['supports'] == (witness is None)
        if witness is None:
            continue
        for field, side in (('outside_write', 'column_off_axis'), ('outside_read', 'row_off_axis')):
            coefficient = witness[field]
            if coefficient is not None:
                role, residue = coefficient
                assert role + 36 in verdict[side]
                assert 0 < residue < body['prime']
    report = {
        'matched_pairs': len(expected),
        'disjoint_stage_masks': sum(row['disjoint_stage_masks'] for row in rational.values()),
        'survivors': exact['survivors'],
        'unresolved': 0,
        'input_sha256': {key: sha256(path.read_bytes()).hexdigest() for key, path in (
            ('price', args.price), ('body_one', args.body_one), ('exact', args.exact))},
    }
    print(dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
