"""Compare the full independent and lead exact R69 support dispositions."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
GEOMETRY = 'a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45'


def read(path):
    raw = path.read_bytes()
    return loads(raw), sha256(raw).hexdigest()


def compare(primary, independent, geometry):
    lead, lead_sha = read(primary)
    local, local_sha = read(independent)
    scope, scope_sha = read(geometry)
    assert lead['head'] == local['head'] == scope['comparator_head'] == HEAD
    assert lead['geometry_sha256'] == local['geometry_sha256'] == scope_sha == GEOMETRY
    assert lead['word_sha256'] == local['word_sha256'] == scope['word_sha256']
    assert lead['price_sha256'] == local['price_sha256'] == scope['price_sha256']
    assert scope['status'] == 'EXHAUSTED' and not scope['unvisited']
    assert len(scope['survivors']) == 454
    assert not (lead['survivors'] or lead['unresolved'] or local['support_only']
                or local['unresolved_coefficients'] or local['unvisited'])
    keys = [[site['h'], *site['move_clocks'], site['clock'], p, q]
            for site in scope['survivors'] for p in site['low'] for q in [None, *site['high']]]
    assert len(keys) == len(set(map(tuple, keys))) == 1193
    for key, before, after in zip(keys, lead['outcomes'], local['decisions'], strict=True):
        assert key == before['key'] == after['key']
        assert before['status'] == 'exterior forward leakage'
        assert after['status'] == 'forward_identity_failed'
        assert after['residual'] and all(Fraction(v) for v in after['residual'].values())
    return dict(head=HEAD, geometry_sha256=scope_sha, primary_sha256=lead_sha,
                independent_sha256=local_sha, geometry_survivors=454, cases_compared=len(keys),
                matching_dispositions=dict(Counter(row['status'] for row in local['decisions'])),
                unique_helpers=len({key[0] for key in keys}), unresolved=0, supported=0)


if __name__ == '__main__':
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument('lead',type=Path)
    p.add_argument('independent',type=Path)
    p.add_argument('geometry',type=Path)
    args = p.parse_args()
    print(dumps(compare(args.lead,args.independent,args.geometry),indent=2,sort_keys=True))
