"""Nominate literal whole-bin exchanges on pinned PR2530's fixed call order.

SciPy MIP nominates only. The separate predecessor literal verifier and complete
native/global/outer replay remain acceptance gates. Apache-2.0.
Prepared for mcorrigan with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=250)
    ap.add_argument('--seconds', type=float, default=3)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = args.source.resolve()
    D = read(source/'evidence/order-screen.json.gz')
    fill = read(source/'evidence/eight-fill.json.gz')
    providers = read(source/'evidence/eight-providers.json')
    widths = providers['gauge44']['widths']
    if any(p['widths'] != widths for p in providers.values()):
        raise ValueError('this bounded search assumes identical provider widths')
    plan = read(args.prepared/'inputs/PLAN.json')
    pairs, sides = plan['pairs'], plan['sides']
    rows = fill['rows']
    bins = defaultdict(list)
    callrows = defaultdict(list)
    family_uses = Counter()
    def family(b):
        rep, child, port = b
        return rep*896+(2*pairs[str(child)]+sides[str(child)])*112+port
    def window(b):
        return D['windows'][f'{b[0]},{b[1]}']
    for i, row in enumerate(rows):
        b = tuple(row[2:5])
        bins[b].append(i)
        callrows[row[0]].append(i)
        family_uses[row[0], family(b)] += 1
    allbins = []
    empty_by_time = defaultdict(list)
    for key, (cap, times) in D['windows'].items():
        rep, child = map(int, key.split(','))
        for port in range(112):
            b = rep, child, port
            allbins.append(b)
            if not bins[b] and cap in (8, 16, 32):
                for t in times:
                    empty_by_time[t].append(b)
    residual = {b: window(b)[0]-sum(widths[rows[i][1]] for i in bins[b]) for b in allbins}
    old_idle = Counter(residual[b] for b in allbins if residual[b])
    old_profile = {int(k): n for k, n in read(source/'PROFILE.json').items()}
    empty8 = [b for b in allbins if window(b)[0] == 8 and not bins[b]]
    a = .0017137379215475043
    price = {r: (r*math.expm1(-a*math.log(r))/a if r else 0.) for r in range(49)}
    best = 0.
    results = []
    started = time.monotonic()
    for attempt in range(min(args.limit, max(1, len(empty8))*3)):
        target = empty8[attempt % len(empty8)]
        ts = window(target)[1]
        t = ts[(len(ts)//2 + (attempt//len(empty8))*3) % len(ts)]
        wanted = [target]
        # A fixed, structural neighbourhood: eight width-eight donors, then
        # complementary widths and available rank-16 stock at the same call.
        by_width = defaultdict(list)
        for i in callrows[t]:
            b = tuple(rows[i][2:5])
            by_width[widths[rows[i][1]]].append(b)
        for w, count in [(8, 6), (7, 3), (4, 3), (5, 2), (9, 4)]:
            bs = sorted(set(by_width[w]), key=lambda b: (residual[b], -window(b)[0], b))
            # Rotate physical donors with the target, without changing scope.
            if bs:
                shift = attempt % len(bs)
                bs = bs[shift:]+bs[:shift]
            wanted.extend(bs[:count])
        wanted.extend(sorted((b for b in empty_by_time[t] if window(b)[0] == 16))[:2])
        wanted = list(dict.fromkeys(wanted))[:24]
        jobs = [i for b in wanted for i in bins[b]]
        selected_uses = Counter((rows[i][0], family(tuple(rows[i][2:5]))) for i in jobs)
        allowed = [set(window(b)[1]) for b in wanted]
        vars_x = []
        jobvars = defaultdict(list)
        binvars = defaultdict(list)
        famvars = defaultdict(list)
        cost = []
        for ji, i in enumerate(jobs):
            t0, helper = rows[i][:2]
            for bi, b in enumerate(wanted):
                if t0 not in allowed[bi] or family_uses[t0, family(b)]-selected_uses[t0, family(b)]:
                    continue
                j = len(cost)
                vars_x.append((ji, bi, j))
                jobvars[ji].append((j, 1))
                binvars[bi].append((j, widths[helper]))
                famvars[t0, family(b)].append((j, 1))
                cost.append(0.)
        zs = {}
        for bi, b in enumerate(wanted):
            zs[bi] = []
            for r in range(window(b)[0]+1):
                j = len(cost)
                zs[bi].append((j, r))
                cost.append(price[r])
        rr, cc, vv, low, high = [], [], [], [], []
        def constrain(items, lo, hi):
            row = len(low)
            for col, value in items:
                if value:
                    rr.append(row); cc.append(col); vv.append(value)
            low.append(lo); high.append(hi)
        for ji in range(len(jobs)):
            constrain(jobvars[ji], 1, 1)
        for bi, b in enumerate(wanted):
            constrain([(j, 1) for j, r in zs[bi]], 1, 1)
            constrain(binvars[bi]+[(j, r) for j, r in zs[bi]], window(b)[0], window(b)[0])
        for items in famvars.values():
            constrain(items, 0, 1)
        matrix = coo_matrix((vv, (rr, cc)), shape=(len(low), len(cost))).tocsc()
        result = milp(np.array(cost), integrality=np.ones(len(cost)), bounds=Bounds(0, 1),
                      constraints=LinearConstraint(matrix, low, high),
                      options={'time_limit': args.seconds, 'mip_rel_gap': 0})
        old_cost = sum(price[residual[b]] for b in wanted)
        gain = old_cost-result.fun if result.x is not None else 0.
        record = dict(attempt=attempt, target=target, time=t, bins=len(wanted), jobs=len(jobs),
                      status=int(result.status), score_gain=float(gain))
        results.append(record)
        if attempt % 10 == 0 or gain > best+1e-8:
            print('SEARCH', json.dumps(record), flush=True)
        if gain > best+1e-8:
            # Integer reconstruction checks every nominated variable and local
            # capacity before publishing a candidate for independent admission.
            xx = np.rint(result.x).astype(int)
            if np.max(np.abs(result.x-xx)) > 1e-5:
                raise ValueError('noninteger incumbent')
            assignment = defaultdict(list)
            for ji, bi, j in vars_x:
                if xx[j]:
                    assignment[bi].append(jobs[ji])
            if sorted(i for v in assignment.values() for i in v) != sorted(jobs):
                raise ValueError('lost or repeated role')
            local_idle = Counter()
            changes = {}
            for bi, b in enumerate(wanted):
                occupied = sum(widths[rows[i][1]] for i in assignment[bi])
                if occupied > window(b)[0]:
                    raise ValueError('overfilled bin')
                rem = window(b)[0]-occupied
                if rem:
                    local_idle[rem] += 1
                offset = 0
                for i in sorted(assignment[bi], key=lambda i: (rows[i][0], rows[i][1])):
                    changes[i] = rows[i][:2]+list(b)+[offset]
                    offset += widths[rows[i][1]]
            newfill = dict(fill, rows=[changes.get(i, row) for i, row in enumerate(rows)])
            delta = Counter(local_idle)
            delta.subtract(residual[b] for b in wanted if residual[b])
            profile = Counter(old_profile)
            profile.update(delta)
            profile = {r: n for r, n in sorted(profile.items()) if n}
            if any(n < 0 for n in profile.values()) or sum(r*n for r, n in profile.items()) != 4816512:
                raise ValueError('invalid global rank mass')
            best = gain
            name = f'candidate-{attempt:03d}'
            (out/(name+'.json.gz')).write_bytes(gzip.compress(json.dumps(newfill,separators=(',',':')).encode(),mtime=0))
            (out/(name+'-profile.json')).write_text(json.dumps(profile))
            (out/(name+'-delta.json')).write_text(json.dumps({r:n for r,n in delta.items() if n}))
            print('NOMINATED', name, 'delta', dict(delta), flush=True)
        (out/'SEARCH.json').write_text(json.dumps(dict(results=results, best_score_gain=best,
            seconds=time.monotonic()-started, scope='bounded nomination, no admission or new kappa'), indent=2))
    print('DONE', len(results), 'best', best, flush=True)


if __name__ == '__main__':
    main()
