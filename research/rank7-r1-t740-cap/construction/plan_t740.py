#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Search provenance (not an entry point of verify.py): how allocation/RELOCATIONS.json was found.

Start: ten lockstep copies of PR #2979's literal T74 fill (lift.py with no relocations). Its pattern mix is ten times
PR2979's T74 mix, which contains 60 non-tight [4,8,9,9,9,9]@48 bins and 17,280 [9,9,9]@32 bins; the optimal face of the
fixed-capacity relaxation (certificates/RELAX-CAP.json of PR2979) has an integral point at T740 that differs only by
    60 x [4,8,9,9,9,9]@48  ->  57 x [9,9,9,9,9]@48 + 3 x []@48
    75 x [9,9,9]@32        ->  60 x [4,9,9,9]@32 + 15 x [8,8,8,8]@32          (both sides tight; widths and bins balance).
The chronology forbids doing this directly (the 4s and 8s of the [4,8,9,9,9,9] bins are late, almost all [9,9,9] bins
close early), so each displaced role travels along a chain of same-width exchanges: it enters an unlocked bin whose
window contains its call and evicts a same-width role of an earlier call, until a target bin can take the last role.
Every intermediate bin keeps its pattern. Steps:
  A  60 fours -> 60 [9,9,9]@32 bins (become [4,9,9,9]);
  B  15 [9,9,9]@32 bins Z (the latest-closing ones) send their 45 nines into 9 early empty @48 bins (5 each);
  C  60 eights -> the Z bins (4 each; become [8,8,8,8]);
  D  three [4,8,9,9,9,9] bins are emptied; their 12 nines go one each into 12 of the other 57;
  E  nine late [9,9,9,9,9]@48 bins are emptied; their 45 nines go one each into the remaining 45 of the 57.
Greedy, seeded (seed 1), first fit; exchanges always move to a strictly earlier call, so chains terminate.

Usage (from the repository root): python3 -B research/rank7-r1-t740-cap/construction/plan_t740.py --out DIR
The search only reads helper widths, windows and families, which PR3015's R1 edit leaves unchanged.
Writes DIR/RELOCATIONS.json and DIR/CHAINS.json and re-checks the rebuilt allocation with PR2979's vendored engine.
Rohan Arun, with substantial AI assistance (Anthropic Claude). Apache-2.0.
"""
import argparse
import collections
import json
import random
import sys
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
SRC = PKG.parent / 'rank7-joint-endframes'
sys.path.insert(0, str(PKG))
import lift as L  # noqa: E402


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seed', type=int, default=1)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    engine = load('owners2979', SRC / 'allocation/vendor/independent_owners.py')
    template, plan = L.read(SRC / 'allocation/vendor/TEMPLATE.json.gz'), L.read(SRC / 'allocation/vendor/PLAN.json.gz')
    providers = L.read(SRC / 'allocation/PROVIDERS.json')
    for pv in providers.values():
        pv['actual_paid_profile'] = {int(r): n for r, n in pv['actual_paid_profile'].items()}
    T, order, dispatch, fill, _ = L.build(SRC / 'allocation', [], providers)
    rows = fill['rows']
    d = {(s, r): p for s, r, p in dispatch}
    win = engine.windows(template, order, T)
    fam = lambda o, c, p: o * 896 + (2 * plan['pairs'][str(c)] + plan['sides'][str(c)]) * 112 + p
    WID = [providers[d[tuple(order[r[0]])]]['widths'][r[1]] for r in rows]
    bins = collections.defaultdict(list)
    used = collections.defaultdict(set)
    for i, (t, h, o, c, p, z) in enumerate(rows):
        bins[o, c, p].append(i)
        used[t].add(fam(o, c, p))
    pattern = lambda b: tuple(sorted(WID[i] for i in bins[b]))
    allbins = [(o, c, p) for (o, c) in win for p in range(112)]
    bypat = collections.defaultdict(list)
    for b in allbins:
        bypat[win[b[0], b[1]][0], pattern(b)].append(b)
    for k in bypat:
        rng.shuffle(bypat[k])
    X = list(bypat[48, (4, 8, 9, 9, 9, 9)])
    assert len(X) == 60
    locked = set(X)

    def fits(i, b):
        t = rows[i][0]
        cap, lo, hi = win[b[0], b[1]]
        return lo < t <= hi and fam(*b) not in used[t]

    chains = []

    def detach(i, label):
        t, h, o, c, p, z = rows[i]
        used[t].discard(fam(o, c, p))
        bins[o, c, p].remove(i)
        rows[i][2:5] = [-1, -1, -1]
        chains.append(dict(step=label, kind='out', role=[t, h], bin=[o, c, p], width=WID[i]))

    def attach(i, b, label):
        assert rows[i][2] == -1 and fits(i, b), (label, i, b)
        t = rows[i][0]
        rows[i][2:5] = list(b)
        bins[b].append(i)
        used[t].add(fam(*b))
        chains.append(dict(step=label, kind='in', role=rows[i][:2], bin=list(b), width=WID[i]))

    exchange = {}

    def chain(i, targets, label, maxhops=40):
        w = WID[i]
        if w not in exchange:
            exchange[w] = sorted((rows[k][0], b, k) for b in allbins if b not in locked for k in bins[b] if WID[k] == w)
        cur = i
        for hop in range(maxhops):
            tgt = next((b for b in targets() if fits(cur, b)), None)
            if tgt is not None:
                attach(cur, tgt, label + ':end')
                return tgt
            t = rows[cur][0]
            nxt = None
            for tt, b, k in exchange[w]:
                if tt >= t:
                    break
                if b in locked or rows[k][2:5] != list(b):
                    continue
                cap, lo, hi = win[b[0], b[1]]
                if lo < t <= hi and fam(*b) not in used[t]:
                    nxt = (b, k)
                    break
            if nxt is None:
                return None
            b, k = nxt
            detach(k, label + ':hop%d' % hop)
            attach(cur, b, label + ':hop%d' % hop)
            locked.add(b)
            cur = k
        return None

    t0 = time.time()
    Y = list(bypat[32, (9, 9, 9)])
    Z = sorted(Y, key=lambda b: -win[b[0], b[1]][2])[:15]
    locked.update(Z)
    for i in [k for b in X for k in bins[b] if WID[k] == 4]:
        detach(i, 'A')
        tgt = chain(i, lambda: [y for y in Y if y not in locked], 'A')
        assert tgt is not None, 'step A'
        locked.add(tgt)
    E48 = [b for b in bypat[48, ()] if b not in locked]
    held = []
    for z in Z:
        for i in list(bins[z]):
            detach(i, 'B')
            held.append(i)
    held.sort(key=lambda i: rows[i][0])
    remaining = list(held)
    for e in E48:
        if not remaining:
            break
        if e in locked:
            continue
        group, calls = [], set()
        cap, lo, hi = win[e[0], e[1]]
        for i in remaining:
            t = rows[i][0]
            if t not in calls and lo < t <= hi and fam(*e) not in used[t]:
                group.append(i)
                calls.add(t)
            if len(group) == 5:
                break
        if len(group) < 5:
            continue
        for i in group:
            attach(i, e, 'B:nine_into_empty48')
            remaining.remove(i)
        locked.add(e)
    assert not remaining
    count = {z: 0 for z in Z}
    for i in [k for b in X for k in bins[b] if WID[k] == 8]:
        detach(i, 'C')
        tgt = chain(i, lambda: [z for z in Z if count[z] < 4], 'C')
        assert tgt is not None, 'step C'
        count[tgt] += 1
    assert all(v == 4 for v in count.values())
    emptied, keep = X[:3], X[3:]
    want = {b: 1 for b in keep}
    open_keep = lambda: [b for b in keep if want[b]]
    nines = [i for b in emptied for i in bins[b] if WID[i] == 9]
    for i in nines:
        detach(i, 'D')
    for i in nines:
        tgt = chain(i, open_keep, 'D')
        assert tgt is not None, 'step D'
        want[tgt] -= 1
    late = [b for b in bypat[48, (9, 9, 9, 9, 9)] if b not in locked]
    late.sort(key=lambda b: -win[b[0], b[1]][1])
    emptied95 = 0
    for b in late:
        if not any(want.values()):
            break
        if b in locked:
            continue
        ns = [i for i in bins[b] if WID[i] == 9]
        if len(ns) != 5:
            continue
        if not all(any(win[k[0], k[1]][1] < rows[i][0] <= win[k[0], k[1]][2] for k in open_keep()) for i in ns):
            continue
        locked.add(b)
        for i in ns:
            detach(i, 'E')
        for i in ns:
            tgt = chain(i, open_keep, 'E')
            assert tgt is not None, 'step E'
            want[tgt] -= 1
        emptied95 += 1
    assert emptied95 == 9 and not any(want.values())
    assert all(r[2] >= 0 for r in rows)
    print('search %.1f s, chain events %d' % (time.time() - t0, len(chains)), flush=True)
    final = {}
    for e in chains:
        if e['kind'] == 'in':
            final[tuple(e['role'])] = e['bin']
    relocations = sorted([t, h] + b for (t, h), b in final.items())
    base_bins = {(r[0], r[1]): (r[2], r[3], r[4]) for r in L.lift_rows(L.read(SRC / 'allocation/FILL.json.gz'))}
    relocations = [e for e in relocations if base_bins[e[0], e[1]] != tuple(e[2:])]
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'RELOCATIONS.json').write_text(json.dumps(relocations, separators=(',', ':')) + '\n')
    (args.out / 'CHAINS.json').write_text(json.dumps(chains, separators=(',', ':')) + '\n')
    T, order, dispatch, fill, touched = L.build(SRC / 'allocation', relocations, providers)
    t0 = time.time()
    result, _, _ = engine.check(T, order, fill, d, None, plan, template, providers)
    print('relocations', len(relocations), 'touched bins', len(touched), 'engine %.1f s' % (time.time() - t0), 'idle', result['idle'], flush=True)


if __name__ == '__main__':
    main()
