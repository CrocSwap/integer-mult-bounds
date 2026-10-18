"""Make the literal doubled T8 owner map used to start the successful search."""
import argparse
import gzip
import json
from collections import Counter
from pathlib import Path

P = Path(__file__).resolve().parent.parent
PRE = P.parent / 'k8-eight-ends'
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
assert not a.out.exists()
plan = json.loads(gzip.decompress((P / 'PLAN.json.gz').read_bytes()))
old = json.loads(gzip.decompress((PRE / 'OWNERS.json.gz').read_bytes()))
roles = []
for g in range(2):
    for z in old:
        roles.append(z | dict(replica=z['replica'] + 8*g, owner_replica=z['owner_replica'] + 8*g,
                              time=2*z['time'] + g, copy=z['copy'] + 896*g,
                              family=z['family'] + 7168*g))
oldplan = json.loads(gzip.decompress((PRE / 'PLAN.json.gz').read_bytes()))
plan['profile'] = {r: 2*n for r, n in oldplan['profile'].items()}
assert plan['order'] == [[s, r+8*g] for s, r in oldplan['order'] for g in range(2)]
used = Counter()
for z in roles:
    cap, times = plan['windows'][str(z['owner_replica']) + ',' + str(z['child'])]
    assert z['time'] in times
    key = z['owner_replica'], z['child'], z['port']
    used[key] += z['width']
    assert used[key] <= cap
a.out.mkdir(parents=True)
(a.out / 'PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
(a.out / 'OWNERS.json.gz').write_bytes(gzip.compress(json.dumps(roles, sort_keys=True,
                                                            separators=(',', ':')).encode(), mtime=0))
print('Doubled', len(old), 'T8 roles to', len(roles), 'T16 roles')
