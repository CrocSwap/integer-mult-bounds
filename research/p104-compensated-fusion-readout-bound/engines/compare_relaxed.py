"""Compare the two complete exact Round 70 disposition receipts."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

LEAD = '34738b6d9031b3170a58f0cb590d81c01ea2c1038810008483d1c24dc7574150'
LABEL = {
    'nonlocal_forward_leakage': 'nonlocal forward leakage',
    'dirty_return_readout_failed': 'dirty return readout failed',
}


def read(path):
    raw = path.read_bytes()
    return loads(raw), sha256(raw).hexdigest()


def compare(primary, independent):
    lead, lead_sha = read(primary)
    local, local_sha = read(independent)
    assert lead_sha == LEAD
    for pin in ('head','word_sha256','price_sha256','geometry_sha256'):
        assert lead[pin] == local[pin]
    assert not (lead['survivors'] or lead['unresolved'] or local['support_only']
                or local['unresolved_coefficients'] or local['unvisited'])
    assert local['cases_visited'] == len(lead['outcomes']) == 1197
    unique = set()
    for before, after in zip(lead['outcomes'], local['decisions'], strict=True):
        assert before['key'] == after['key']
        assert before['status'] == LABEL[after['status']]
        assert after['residual'] and all(Fraction(value) for value in after['residual'].values())
        unique.add(tuple(after['key']))
    assert len(unique) == 1197
    counts = Counter(row['status'] for row in local['decisions'])
    assert counts == {'nonlocal_forward_leakage':820, 'dirty_return_readout_failed':377}
    return dict(head=local['head'], price_sha256=local['price_sha256'],
                geometry_sha256=local['geometry_sha256'], primary_sha256=lead_sha,
                independent_sha256=local_sha, paired_keys=len(unique), matching_dispositions=dict(counts),
                supported=0, unresolved=0)


if __name__ == '__main__':
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument('primary',type=Path)
    p.add_argument('independent',type=Path)
    args=p.parse_args()
    print(dumps(compare(args.primary,args.independent),sort_keys=True,indent=2))
