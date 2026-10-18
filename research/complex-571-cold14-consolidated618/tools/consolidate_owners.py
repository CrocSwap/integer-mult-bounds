"""Discovery only: consolidate literal helpers without changing their providers.

Every move preserves the whole-helper rule, capacity and window membership.
The package's independent physical replay remains the admission criterion.
Prepared with OpenAI Codex assistance; based on PR610's credited owner map.
"""
import argparse
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def repack(plan, roles):
    bins = {}
    for key, (cap, times) in plan['windows'].items():
        o, ch = map(int, key.split(','))
        for port in range(112):
            fam = o * 896 + (2 * plan['pairs'][str(ch)] + plan['sides'][str(ch)]) * 112 + port
            bins[o, ch, port] = dict(cap=cap, times=set(times), roles=[], family=fam, left=cap)
    occupied = defaultdict(set)
    for i, r in enumerate(roles):
        b = bins[r['owner_replica'], r['child'], r['port']]
        b['roles'].append(i)
        b['left'] -= r['width']
        assert r['time'] not in occupied[b['family']]
        occupied[b['family']].add(r['time'])
    psi = [0] + [r * math.log(73 / r) for r in range(1, 49)]
    moves = []
    while True:
        partial = [(k,b) for k,b in bins.items() if 0 < b['left'] < b['cap']]
        best = None
        for sk, s in partial:
            for i in s['roles']:
                r = roles[i]; w = r['width']; t = r['time']
                for dk, d in partial:
                    if sk == dk or d['left'] < w or t not in d['times'] or t in occupied[d['family']]:
                        continue
                    gain = psi[s['left']] + psi[d['left']] - psi[s['left'] + w] - psi[d['left'] - w]
                    if gain > 1e-9 and (best is None or gain > best[0]):
                        best = gain, sk, dk, i
        if best is None:
            break
        gain, sk, dk, i = best
        s, d, r = bins[sk], bins[dk], roles[i]
        occupied[s['family']].remove(r['time']); occupied[d['family']].add(r['time'])
        s['roles'].remove(i); d['roles'].append(i)
        s['left'] += r['width']; d['left'] -= r['width']
        r.update(owner_replica=dk[0], child=dk[1], port=dk[2], copy=dk[0]*112+dk[2], family=d['family'])
        moves.append(dict(time=r['time'], helper=r['helper'], width=r['width'], source=sk, destination=dk, entropy_gain=gain))
    for b in bins.values():
        offset = 0
        for i in sorted(b['roles'], key=lambda i: (roles[i]['time'], roles[i]['helper'])):
            roles[i]['offset'] = offset
            offset += roles[i]['width']
        assert offset + b['left'] == b['cap']
    paid = Counter()
    for c in plan['provider_calls']:
        paid.update({int(r): n for r,n in plan['provider_registry'][c['provider']]['actual_paid_profile'].items()})
    paid.update(b['left'] for b in bins.values() if b['left'])
    assert 73 * plan['live'] - sum(r*n for r,n in paid.items()) == plan['deficit']
    plan['profile'] = {str(r): n for r,n in sorted(paid.items())}
    return plan, roles, moves


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: discovery checks require assertions')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    plan_raw = (a.data/'PLAN.json').read_bytes(); owners_raw = (a.data/'OWNERS.json.gz').read_bytes()
    plan, roles, moves = repack(json.loads(plan_raw), json.loads(gzip.decompress(owners_raw)))
    a.out.mkdir(parents=True, exist_ok=False)
    plan.update(mode='literal-partial-owner-consolidation', solver_status='GREEDY_FEASIBLE_NOT_OPTIMAL', gap=None,
                source_plan_sha256=hashlib.sha256(plan_raw).hexdigest(), source_owners_sha256=hashlib.sha256(owners_raw).hexdigest())
    raw = json.dumps(roles,sort_keys=True,separators=(',',':')).encode()
    plan['assignment_sha256'] = hashlib.sha256(raw).hexdigest()
    (a.out/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    (a.out/'PLAN.json').write_text(json.dumps(plan,indent=1)+'\n')
    receipt = dict(status='DISCOVERY_REQUIRES_INDEPENDENT_ADMISSION', moves=moves, entropy_gain=sum(m['entropy_gain']for m in moves), profile=plan['profile'])
    (a.out/'SEARCH.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
