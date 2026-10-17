"""Cross-copy idle-axis hosting for #433's compressed nine-stage complex template (m=73, R=560, rank-nine residuals),
on top of #442's windows.  Residuals of a child are laid along the concatenated pending sets of its 120 port copies;
a residual may be split across two ports (two data families of the same child, same window).  Unhosted residuals are
re-tiled eight per bank with one paid pad.  usage: complex_split.py SPLIT_CENTRES_DIR OUT [--discover]"""
import gzip, hashlib, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import tape_core as TC
V, K, T, L, M, R = 120, 4, 8, 9, 73, 560
DATA = 2 * K * V * T
DISCOVER = False
def main(src, out):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((src / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    integ = json.loads((src / 'INTEGRATION.json').read_text()); checks = json.loads((src / 'LOCAL-CHECKS.json').read_text())
    assert hashlib.sha256(blob).hexdigest() == integ['global_template_sha256'] and t['live'] == integ['live']
    rank = {}
    for it in t['idle_children']:
        assert it['replicas'] == T; rank.setdefault(it['child'], it['rank']); assert rank[it['child']] == it['rank']
    pair_of_stage = {e['stage']: e['pair'] for e in t['recipe'] if e['kind'] == 'local'}
    sched = []; side_of = {}; pair_of = {}
    for e in t['execution_schedule']:
        if e['kind'] == 'local_cover_sweep': sched.append(dict(kind='local', stage=e['stage'], pair=pair_of_stage[e['stage']]))
        elif e['kind'] == 'bridge': sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
        elif e['kind'] == 'idle_cover_sweep':
            for sd, ch in enumerate(e['child_indices']):
                if ch in rank:
                    sched.append(dict(kind='idle', pair=e['pair'], rank=rank[ch], idx=ch)); side_of[ch] = sd; pair_of[ch] = e['pair']
    win = {k: x for k, x in TC.windows(sched).items() if x[1] > 0 and x[2]}
    avail = {(s, 9): R for s in range(L)}
    sel = HERE / 'SELECTION.json'; key = 'complex'
    if DISCOVER:
        counts, val = TC.solve(win, V, avail, M, [9], dict(vars=lambda st: [], rows=lambda *a: []))
        TC.save(sel, key, counts, val)
    counts, val = TC.load(sel, key)
    pieces, rem = TC.expand(win, counts, {s: [(h, 9) for h in range(R)] for s in range(L)}, V)
    base = [DATA]; tile = {}; partial = Counter()
    for s in range(L):
        left = [(rep, h) for rep in range(T) for h in range(R) if (s, h) not in pieces]
        for z, (rep, h) in enumerate(left): tile[s, rep, h] = divmod(z, 8)
        nb = -(-len(left) // 8); base.append(base[-1] + nb)
        if len(left) % 8: partial[M - 9 * (len(left) % 8)] += 1
        partial[M - 72] += len(left) // 8
    W = base[-1]; split = 0
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for h in range(R):
            if (s, h) in pieces:
                i, segs = pieces[s, h]; fam = lambda port: rep * 960 + (2 * pair_of[i] + side_of[i]) * V + port
                if len(segs) == 1:
                    port, off, w = segs[0]; own.append([fam(port), [3, i, off]])
                else:
                    (p1, o1, w1), (p2, o2, w2) = segs; own.append([fam(p1), [5, i, o1, w1, fam(p2), o2, w2]]); split += 1
            else:
                b, sl = tile[s, rep, h]; own.append([base[s] + b, [2, sl]])
        assert len({(f, tuple(r)) for f, r in own}) == 2 * V + R and all(f < W for f, r in own)
        c['owners'] = own
    paid = Counter()
    for c in t['calls']:
        for r_, z in checks[c['orientation']]['paid_profile'].items(): paid[int(r_)] += z
    newidle = []
    for it in t['idle_children']:
        ch, port = it['child'], it['port']; rr = rem.get((ch, port), it['rank']) if ch in win else it['rank']
        if rr: newidle.append(dict(child=ch, port=port, rank=rr, hosted=it['rank'] - rr, replicas=T)); paid[rr] += T
    for r_, n in partial.items(): paid[r_] += n
    mass = sum(r * n for r, n in paid.items()); D = M * W - mass; assert D == 2496, D
    t.update(version='hamming-mutable-basis-nine-v1+idle-axis-hosting+cross-copy', live=W, idle_children=newidle,
             physical=W + R + (integ['physical'] - integ['live'] - R),
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()}, sides=side_of, pairs=pair_of,
                          pieces=[[s, h, i, [list(x) for x in segs]] for (s, h), (i, segs) in sorted(pieces.items())],
                          banks=[base[s + 1] - base[s] for s in range(L)]))
    t['bank_padding']['families'] = list(range(DATA, W)); t['cover_final_correction']['families'] = [0, W]
    t['cover_final_correction']['charged_calls_per_cover'] = W
    for e in t['execution_schedule']:
        if e['kind'] == 'bank_padding_cover_sweep': e['families'] = [DATA, W]
        elif e['kind'] == 'translate_every_live_family': e.update(t['cover_final_correction'])
    tb = json.dumps(t, sort_keys=True, separators=(',', ':')).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(status='PASS_CROSS_COPY_HOSTED_COMPLEX_TEMPLATE', parent_template_sha256=integ['global_template_sha256'],
               template_sha256=hashlib.sha256(tb).hexdigest(), live=W, physical=t['physical'], global_profile=dict(sorted(paid.items())),
               rank_mass=mass, deficit=D, maxchild=max(paid), hosted_residuals=len(pieces) * T, split_residuals=split,
               banks_per_stage=t['hosting']['banks'], saved_cost_proxy=val, seconds=time.monotonic() - t0)
    (out / 'HOSTED.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'split_residuals', 'banks_per_stage', 'deficit', 'global_profile')}))
if __name__ == '__main__':
    DISCOVER = '--discover' in sys.argv; args = [a for a in sys.argv[1:] if a != '--discover']
    main(Path(args[0]), Path(args[1]))
