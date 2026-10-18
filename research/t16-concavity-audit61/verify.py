#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact source-bound comparison of four admitted T16 residual histograms."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRS = (1022, 1028, 1031, 1042)
BASE = 'ba82555c64e1879e4b7decce28186f208fcb8262'
PREFIX = 'research/community-batch1047-audit/variants'
REQUIRED = tuple(f'{PREFIX}/pr{pr}/research/gauge44-slots-t16/data/{name}'
                 for pr in PRS for name in ('PLAN.json', 'OWNERS.json.gz')) + (
    'research/gauge44-slots-t16/hosting/PROOF.md',
    'research/gauge44-slots-t16/data/PLAN.json',
    'research/gauge44-slots-t16/data/OWNERS.json.gz',
    'docs/research/community-batch1047-review.md',)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(json.loads(json.dumps(x)), sort_keys=True, separators=(',', ':'), allow_nan=False)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def digest(path):
    data = path.read_bytes()
    if path.suffix != '.gz':
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()


def check_sources(root=ROOT, here=HERE):
    pins = read(here / 'SOURCES.json')
    require(pins['base_commit'] == BASE, 'base commit')
    require(set(pins['files']) == set(REQUIRED), 'exact source inventory')
    for rel in REQUIRED:
        require(digest(root / rel) == pins['files'][rel], 'source hash: ' + rel)
    require(digest(here / 'BASE-SELECTED.json') == pins['selected_snapshot_sha256'], 'selected snapshot hash')
    selected = read(here / 'BASE-SELECTED.json')
    require('1042' in canonical(selected) and '1672188119205421' in canonical(selected), 'selected snapshot claim')
    for name in ('PLAN.json', 'OWNERS.json.gz'):
        a = root / f'{PREFIX}/pr1042/research/gauge44-slots-t16/data/{name}'
        b = root / f'research/gauge44-slots-t16/data/{name}'
        require(canonical(read(a)) == canonical(read(b)), 'selected map binding')


def reconstruct(plan, roles):
    require((plan['T'], plan['M'], plan['live'], plan['deficit']) == (16, 73, 14336, 5120), 'dimensions')
    widths = plan['provider_registry']['gauge44']['widths']
    require(len(widths) == 480 and all(type(x) is int and x > 0 for x in widths), 'whole widths')
    order = [tuple(x) for x in plan['order']]
    require(len(order) == 144 and set(order) == {(s, r) for s in range(9) for r in range(16)}, 'call inventory')
    require(len(roles) == 69120, 'role count')
    occupied, seen, families, sums = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(int)
    for r in roles:
        t, h = r['time'], r['helper']
        require(type(t) is int and 0 <= t < 144 and (r['stage'], r['replica']) == order[t], 'call address')
        require(type(h) is int and 0 <= h < 480 and h not in seen[t], 'helper inventory')
        seen[t].add(h)
        require(r['family'] not in families[t], 'duplicate family')
        families[t].add(r['family'])
        w, off = r['width'], r['offset']
        require(type(w) is int and w == widths[h], 'whole width binding')
        require(type(off) is int and off >= 0 and type(r['port']) is int and 0 <= r['port'] < 112, 'slice coordinates')
        key = (r['owner_replica'], r['child'], r['port'])
        cap, times = plan['windows'][f'{key[0]},{key[1]}']
        require(t in times and off + w <= cap, 'window/capacity')
        cells = set(range(off, off + w))
        require(not occupied[key] & cells, 'overlapping slices')
        occupied[key].update(cells)
        sums[key] += w
    require(len(seen) == 144 and all(len(x) == 480 for x in seen.values()), 'complete calls')
    hist = Counter()
    for key, (cap, _) in plan['windows'].items():
        owner, child = map(int, key.split(','))
        for port in range(112):
            group = (owner, child, port)
            require(occupied[group] == set(range(sums[group])), 'non-prefix')
            hist[cap - sums[group]] += 1
    require(sum(hist.values()) == 32256 and sum(r*n for r,n in hist.items()) == 237024, 'residual size/mass')
    paid = Counter({int(r): n for r,n in plan['profile'].items()})
    paid.subtract({r:n for r,n in hist.items() if r})
    require(all(n >= 0 and n % 144 == 0 for n in paid.values()), '144 local profiles')
    require(sum(int(r)*n for r,n in plan['profile'].items()) == 73*14336-5120, 'global rank mass')
    return dict(histogram=dict(sorted(hist.items())), local_profile={r:n//144 for r,n in sorted(paid.items()) if n},
                roles=len(roles), residual_count=sum(hist.values()), residual_rank=sum(r*n for r,n in hist.items()))


def floor_root(n, degree):
    lo, hi = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**degree <= n:
            lo = mid
        else:
            hi = mid
    return lo if hi**degree > n else hi


def power_interval(delta, degree, scale=10**12):
    """Bounds sum delta[r]*r**(1/degree); common positive 73**b omitted."""
    lower = upper = 0
    for r, count in delta.items():
        if r == 0 or count == 0:
            continue
        n = r * scale**degree
        lo = floor_root(n, degree)
        require(lo**degree <= n < (lo+1)**degree, 'root enclosure')
        hi = lo if lo**degree == n else lo+1
        lower += count * (lo if count > 0 else hi)
        upper += count * (hi if count > 0 else lo)
    require(lower <= upper, 'interval ordering')
    return dict(lower_numerator=lower, upper_numerator=upper, denominator=scale,
                sign='negative' if upper < 0 else 'positive' if lower > 0 else 'unresolved')


def compare(old, new):
    require(sum(old.values()) == sum(new.values()), 'equal residual count including zero')
    require(sum(r*n for r,n in old.items()) == sum(r*n for r,n in new.items()), 'equal mass')
    delta = {r:new.get(r,0)-old.get(r,0) for r in sorted(set(old)|set(new))}
    delta = {r:n for r,n in delta.items() if n}
    margins = [sum(max(r-k,0)*n for r,n in delta.items()) for k in range(49)]
    relation = 'new_majorizes_old' if min(margins) >= 0 else 'old_majorizes_new' if max(margins) <= 0 else 'incomparable'
    witnesses = []
    for k in sorted({margins.index(min(margins)), margins.index(max(margins))}):
        if margins[k]:
            witnesses.append(dict(threshold=k, cost='min(r,k)', new_minus_old=-margins[k]))
    return dict(delta=delta, stop_loss_new_minus_old=margins, relation=relation, concave_witnesses=witnesses,
                power_cost_b_half=power_interval(delta,2), power_cost_b_three_quarters=power_interval(delta,4))


def build(root=ROOT):
    results, plans = {}, {}
    for pr in PRS:
        folder = root / f'{PREFIX}/pr{pr}/research/gauge44-slots-t16/data'
        plan = read(folder/'PLAN.json')
        plans[pr] = plan
        results[pr] = reconstruct(plan, read(folder/'OWNERS.json.gz'))
    require(all(plans[p]['windows'] == plans[1022]['windows'] and plans[p]['order'] == plans[1022]['order'] for p in PRS), 'common geometry/order')
    require(all(plans[p]['provider_registry']['gauge44']['widths'] == plans[1022]['provider_registry']['gauge44']['widths'] for p in PRS), 'common whole widths')
    require(all(results[p]['local_profile'] == results[1022]['local_profile'] for p in PRS), 'same local paid word')
    pairs = {f'{a}->{b}':compare(results[a]['histogram'],results[b]['histogram']) for i,a in enumerate(PRS) for b in PRS[i+1:]}
    require(sum(x['relation'] == 'incomparable' for x in pairs.values()) == 5 and
            pairs['1028->1031']['relation'] == 'new_majorizes_old', 'frozen comparison outcomes')
    selected = pairs['1031->1042']
    require(selected['power_cost_b_half']['sign'] == 'negative' and
            selected['power_cost_b_three_quarters']['sign'] == 'positive', 'selected power-cost reversal')
    return dict(schema='t16-concavity-audit/1', base_commit=BASE, maps=results, comparisons=pairs,
                scope='Four frozen reviewed T16 maps only; no new supplier, feasibility admission, optimizer optimum, or kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    check_sources()
    result = build()
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        require(not path.exists(), 'refusing certificate overwrite')
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    require(canonical(read(path)) == canonical(result), 'certificate mismatch')
    print('PASS_T16_CONCAVITY_AUDIT: 276480 roles; six pairs; five incomparable; selected power-cost reversal')


if __name__ == '__main__':
    main()
