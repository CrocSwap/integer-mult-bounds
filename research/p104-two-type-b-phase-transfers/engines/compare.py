"""Compare all modular and independent exact two-transfer dispositions."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path


def clock_key(key):
    return tuple(sorted(key['odd']+key['even']))


def compare(root):
    price = (root/'PRICE.json').read_bytes()
    p = loads(price)
    body = loads((root/'BODY1.json').read_bytes())
    exact = loads((root/'independent/RESULT.json').read_bytes())
    assert sha256(price).hexdigest() == body['price_sha256'] == exact['price_sha256']
    assert p['head'] == body['head'] == exact['comparator_head']
    assert p['caller_head'] == body['caller_head'] == exact['caller_head']
    assert exact['old_endpoint_columns'] == 36
    assert not any((body['unvisited'], body['survivors'], exact['unvisited'], exact['survivors']))
    keys = [clock_key(k) for k in p['keys']]
    first = body['results']
    second = {tuple(r['key']):r for r in exact['records']}
    assert len(keys) == len(set(keys)) == len(first) == len(second) == body['visited'] == exact['tested'] == 1950
    assert keys == [clock_key(r['key']) for r in first]
    assert set(keys) == set(second)
    for key, row in zip(keys,first,strict=True):
        assert tuple(row['chronological']) == key
        m = row['mismatch']
        assert m['body_index'] == 0 and 0 <= m['row'] < 36 and 0 <= m['column'] < 36
        assert 0 <= m['left'] < body['prime'] and 0 <= m['right'] < body['prime'] and m['left'] != m['right']
        i,j,v = second[key]['first_difference']
        assert 36 <= i < 72 and 36 <= j < 72 and Fraction(v)
    return {'head':p['head'],'caller_head':p['caller_head'],'all_keys_matched':len(keys),
            'independent_old_columns':36,'body_one_survivors':0,
            'unresolved':0,'whole_optimistic_upper':p['whole_optimistic_upper'],
            'compatible_saving_in_scope':0}


if __name__ == '__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args=parser.parse_args()
    print(dumps(compare(args.root),indent=2,sort_keys=True))
