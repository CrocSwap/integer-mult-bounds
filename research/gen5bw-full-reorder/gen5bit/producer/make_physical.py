#!/usr/bin/env python3
"""Physical layer producer for a raw paired-cube bit word (PR168 format): compensated late reuse pairs.

Input dir: graph_p12.json word_p12.json frames_p12.json kchron_p12.json profile_p12.json (raw generator output).
Output dir: same names, word gains op_frame (= node frames unless --descent), pairs [[donor, recipient]],
reads {recipient: absolute execution position}; frames/word also written gzipped for PR200's Candidate.

Pair rules (PR200 bit/word.py + base_word.py): recipient gauged, read right before its first op; donor
ungauged, non-root, non-source, last op strictly before that read; donor last op frame inside the recipient
gauge frame; both nondegenerate; one-to-one; per-target gauge read times monotone along the nested chain.
Prepared by DreamingOfClouds with Anthropic Claude assistance; Apache-2.0.
"""
import argparse, gzip, json, sys, importlib.util, time
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHK = HERE.parent / 'references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def hopcroft_karp(adj, nleft):
    INF = 1 << 30
    matchL = [-1] * nleft; matchR = {}
    from collections import deque
    while True:
        dist = [INF] * nleft; q = deque()
        for u in range(nleft):
            if matchL[u] < 0: dist[u] = 0; q.append(u)
        found = False
        while q:
            u = q.popleft()
            for w in adj[u]:
                v2 = matchR.get(w, -1)
                if v2 < 0: found = True
                elif dist[v2] == INF: dist[v2] = dist[u] + 1; q.append(v2)
        if not found: break
        sys.setrecursionlimit(100000)
        def dfs(u):
            for w in adj[u]:
                v2 = matchR.get(w, -1)
                if v2 < 0 or (dist[v2] == dist[u] + 1 and dfs(v2)):
                    matchL[u] = w; matchR[w] = u; return True
            dist[u] = INF; return False
        for u in range(nleft):
            if matchL[u] < 0: dfs(u)
    return matchL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--ranks', default='21', help='gauge dims allowed as recipients, comma list')
    ap.add_argument('--bank-parity', action='store_true', help='drop the last pair if the 60-replica bank tiling would have odd total width')
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    mod = load('chk', CHK)
    C = mod.Checker(src, 12)
    C.frames(); C.decoder(); C.geometry()
    g, w = C.g, C.w
    ops = w['ops']; v = g['v']
    R = 1 + max(max(x, y) for x, y, _ in ops)
    nf = {int(k): f for k, f in w['node_frame'].items()}
    opframe = [nf[n] for _, _, n in ops]
    phase1 = sorted(w['phase1']); ph = set(phase1)
    rest = [i for i in range(len(ops)) if i not in ph]
    pos = {i: p for p, i in enumerate(rest)}
    role_ops = defaultdict(list)
    for i in phase1 + rest:
        for s in ops[i][:2]: role_ops[s].append(i)
    assert all(xs == sorted(xs) for xs in role_ops.values())
    first = {s: pos.get(xs[0], -1) for s, xs in role_ops.items()}
    last = {s: pos.get(xs[-1], -1) for s, xs in role_ops.items()}
    endframe = {s: opframe[xs[-1]] for s, xs in role_ops.items()}
    gauge = {z['role']: z for z in w['gauges']}
    roots = set(w['rootroles']); sources = set(w['sources'].values())
    allowed = {int(x) for x in a.ranks.split(',')}
    # per-target chain order of gauges (time order = reversed selection order)
    chain = defaultdict(list)
    for z in reversed(w['gauges']):
        for t in z['targets']: chain[t].append(z['role'])
    # recipients: allowed dims; a recipient must be the LAST gauge of each of its targets' chains unless
    # every later gauge on that target is also a recipient (resolved iteratively below: start with tops)
    recips = [b for b in gauge if gauge[b]['dim'] in allowed]
    def ok(b):
        fb = gauge[b]['frame']
        for t in gauge[b]['targets']:
            later = chain[t][chain[t].index(b) + 1:]
            if any(not (C.sub(gauge[x]['frame'], fb) and C.sub(fb, gauge[x]['frame'])) for x in later): return False
        return True
    recips = [b for b in recips if ok(b)]
    donors = [s for s in range(R) if s not in gauge and s not in roots and s not in sources and s in role_ops]
    print('roles', R, 'gauges', len(gauge), 'recipient candidates', len(recips), 'donor candidates', len(donors), flush=True)
    t0 = time.time()
    nd_cache = {}
    def nondeg(f):
        r = nd_cache.get(f)
        if r is None: r = nd_cache[f] = C.nondeg(f)
        return r
    # group donors by end frame to share containment tests
    by_frame = defaultdict(list)
    for d in donors:
        if nondeg(endframe[d]): by_frame[endframe[d]].append(d)
    print('donor end frames', len(by_frame), 'nondeg donors', sum(map(len, by_frame.values())), flush=True)
    adj = []
    for b in recips:
        gb = gauge[b]['frame']; rt = first[b]
        lst = []
        if nondeg(gb):
            for f, ds in by_frame.items():
                if C.dimf[f] > C.dimf[gb]: continue
                cand = [d for d in ds if last[d] < rt]
                if cand and C.sub(f, gb): lst.extend(cand)
        adj.append(lst)
    print('edges', sum(map(len, adj)), 'recipients with an edge', sum(1 for x in adj if x), 'secs', round(time.time() - t0, 1), flush=True)
    m = hopcroft_karp(adj, len(recips))
    pairs = [[m[i], b] for i, b in enumerate(recips) if m[i] >= 0]
    if a.bank_parity:
        # residual family widths: 24 - dim for non-recipient gauges, 24 for every other physical role
        matched = {b for _, b in pairs}
        width = sum(24 - gauge[g]['dim'] for g in gauge if g not in matched) + 24 * (R - len(pairs) - (len(gauge) - len(matched)))
        if width % 2:
            dropped = pairs.pop()
            # dropping a pair returns its recipient (rank d) to the entrances and its donor slot to the plain
            # helpers: the width changes by (24 - d) + 24, which is odd exactly when d is odd (default rank 21)
            assert (24 - gauge[dropped[1]]['dim']) % 2 == 1, 'bank parity not restored'
            print('bank parity: dropped pair', dropped, flush=True)
    print('pairs', len(pairs), flush=True)
    reads = {str(b): len(phase1) + first[b] for d, b in pairs}
    W = dict(w); W['op_frame'] = opframe; W['pairs'] = pairs; W['reads'] = reads
    W['descent'] = 'none: op_frame[i] = node_frame[ops[i][2]]'
    W['reuse'] = 'late compensated reuse: recipient slot is the donor register; recipient old-value read right before its first op, after the donor last op'
    for name in ('graph', 'frames', 'kchron', 'profile'):
        (out / ('%s_p12.json' % name)).write_text((src / ('%s_p12.json' % name)).read_text())
    (out / 'word_p12.json').write_text(json.dumps(W, sort_keys=True))
    for name in ('word', 'frames'):
        raw = (out / ('%s_p12.json' % name)).read_bytes()
        (out / ('%s_p12.json.gz' % name)).write_bytes(gzip.compress(raw, mtime=0))
    (out / 'sinks.json').write_text('[]')
    print(json.dumps(dict(pairs=len(pairs), physical_R=R - len(pairs), dims=Counter(gauge[b]['dim'] for _, b in pairs))))


if __name__ == '__main__':
    main()
