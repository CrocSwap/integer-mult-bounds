#!/usr/bin/env python3
"""One-child bit profile of Swapnil Jain's round-seven deferred word (h=23), under PR104's opposite-bank rule.

Reads the two frozen round-seven data files (not vendored; pinned by SHA-256 below) from a directory given on
the command line, e.g. a checkout of https://github.com/Swapnil-jain/integer-mult-kappa at
741e7aa078392553815df7926ee17ac5e25a8c38 (certificates/round7/), or PR97's imported copy
(research/deferred-signed/swapnil-round7/certificates/round7/). The frame dimensions are the ones recorded in
the data file; Swapnil's check_frames.py re-derives each of them exactly and PR97 replays the word.

Every projector residual of rank r is one child of width r (PR104, notes/stopped-product-factorization.tex):
  each slot: its chain steps from the deferral frame sigma_u to F, and one exterior child m - (h - dim sigma_u);
  each retained centre: one copied transform of width h-1;
  each target y_T: its chain 0 -> deferred readout levels -> t_T^perp;  each data wire X_S: its chain of V frames;
  each data pair: one data residual of width (h-1)^2 and one endpoint copy.
Usage: python3 research/deferred-stopped/bit_round7.py DIR      (writes bit-profile.json next to this file)
Prepared by Avi Eisenberg (ikeboy) with Anthropic Claude assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {'witness_23.json.gz': 'b2486aa2bb222bacea6e52162a3920780e45dd8edc5d7cb03eabea336a1c6588',
        'deferred_23.json.gz': '8c38e947ff9e021e308000dd82bb5e2194eb265d8b75194e22ce783d3e75317c'}


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def main(directory):
    data = {}
    for name, digest in PINS.items():
        raw = (Path(directory) / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, 'pinned hash of ' + name)
        data[name] = json.loads(gzip.decompress(raw))
    W, D = data['witness_23.json.gz'], data['deferred_23.json.gz']
    h = D['h']; R = D['R']; trip = list(combinations(range(h), 3)); v = len(trip); m = h * h; N = v * v
    tid = {T: i for i, T in enumerate(trip)}
    args = {int(n): (tuple(a) if a else None) for n, a in W['args'].items()}
    late = {int(n): (list(e), list(l)) for n, (e, l) in W['late'].items()}
    ops = [tuple(o[:2]) + (tuple(o[2]),) if o[0] == 'fan' else tuple(o) for o in D['ops']]
    hold, start = D['hold'], D['start']
    out = {s: (c, tuple(T)) for s, c, T in D['out']}; ret = {s: c for s, c in D['ret']}
    sigma = dict(zip(D['readout_order'], D['sigma'])); sel = set(D['readout_order'])
    f = [0] * R
    for s, B in sigma.items(): f[s] = len(B)
    vstart = dict(zip(D['vleaf_slots'], D['vleaf_start']))
    node_dims = {n: d for n, d in D['node_dims']}
    late_dims = {(n, tuple(lt)): d for n, lt, d in D['late_dims']}
    pivslot = {o[3]: o[1] for o in ops if o[0] == 'add'}

    def start_key(s):
        n0 = hold[s][0]
        if args[n0] is None: return ('v', s)
        st = start[s]; k = st[2] if len(st) > 2 else None; dec = late.get(n0)
        if dec is None or k in dec[0]: return ('n', n0)
        lt = dec[1]; return ('c', n0, tuple(lt[lt.index(k):]))

    def chain(s):
        ch = [('sigma', s) if s in sel else ('0',), start_key(s)]
        for idx, n in enumerate(hold[s]):
            if idx > 0: ch.append(('n', n))
            if args[n] is not None and pivslot.get(n) == s and n in late:
                lt = late[n][1]
                for i in range(len(lt) - 1): ch.append(('c', n, tuple(lt[i:])))
        if s in out: ch.append(('out',))
        if s in ret: ch.append(('ret',))
        ch.append(('F',)); return ch

    def dim(key):
        k = key[0]
        if k == '0': return 0
        if k == 'F': return h
        if k in ('out', 'ret'): return h - 1
        if k == 'n': return node_dims[key[1]]
        if k == 'c': return late_dims[key[1], key[2]]
        if k == 'sigma': return f[key[1]]
        if k == 'v': return len(vstart[key[1]])
        raise KeyError(key)

    # garbage supports (transpose sweep) for the deferred levels on each target
    cov = [set() for _ in range(R)]
    for s, (c, T) in out.items(): cov[s].add(tid[T])
    for s, c in ret.items(): cov[s].update(t for t, T in enumerate(trip) if c in T)
    for o in reversed(ops):
        if o[0] == 'add': cov[o[2]] |= cov[o[1]]
        elif o[0] == 'fan':
            for g in o[2]: cov[o[1]] |= cov[g]
    levels = defaultdict(set)
    for s in sel:
        for t in cov[s]: levels[t].add(f[s])

    z = Counter()
    for s in range(R):
        ds = [dim(k) for k in chain(s)]
        require(all(b >= a for a, b in zip(ds, ds[1:])) and ds[-1] == h, 'monotone chain %d' % s)
        for a, b in zip(ds, ds[1:]):
            if b > a: z[b - a] += 2 * v
        z[m - (h - f[s])] += 2 * v
    z[h - 1] += 2 * v * h
    for t in range(v):
        ls = sorted(levels[t] | {0, h - 1})
        for a, b in zip(ls, ls[1:]): z[b - a] += 2 * v
    for n, us in D['xs_order']:
        ds = [1] + [len(vstart[s]) for s in us] + [h]
        ds = [d for i, d in enumerate(ds) if i == 0 or d != ds[i - 1]]
        require(all(b > a for a, b in zip(ds, ds[1:])), 'data-wire chain')
        for a, b in zip(ds, ds[1:]): z[b - a] += 2 * v
    z[(h - 1) ** 2] += 2 * N
    z[1] += N
    Wb = 2 * N + 2 * v * R; L = 2 * v * h * (h - 1); s_ = Wb * m - N + L
    require(sum(t * c for t, c in z.items()) == s_, 'bit rank mass')
    require(all(0 < t < m for t in z), 'children below m')
    prof = dict(h=h, v=v, R=R, m=m, N=N, W=Wb, L=L, total_rank=s_, deficit=N - L, maxchild=max(z),
                deferred_slots=len(sel), source=dict(repository='https://github.com/Swapnil-jain/integer-mult-kappa',
                commit='741e7aa078392553815df7926ee17ac5e25a8c38', sha256=PINS),
                child_multiplicities=dict(sorted(z.items())))
    (HERE / 'bit-profile.json').write_text(json.dumps(prof, indent=1) + '\n')
    print('PASS bit: R=%d, deferred slots %d, maxchild %d, rank mass %d' % (R, len(sel), max(z), s_))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
