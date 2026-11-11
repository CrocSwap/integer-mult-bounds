"""Cross-copy idle-axis hosting for #434's compressed nine-stage bit template (m=64), on top of #442's windows.
Every residual of a child is laid along the concatenated pending sets of that child's 240 copies; a residual may be
split across two copies (two data families of the same child, same window).  Unhosted residuals keep #442's exact
width-64 bank tiling.  usage: bit_split.py PARENT_GLOBAL_DIR LOCAL_CHECK_DIR OUT [--discover]"""
import gzip, hashlib, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import tape_core as TC
H, V, R, L, K, T, M = 8, 120, 747, 9, 4, 8, 64
DATA = 2 * K * V * T
DISCOVER = False
def tiling_vars(stages): return [('a', s) for s in stages] + [('b', s) for s in stages] + [('c', s) for s in stages]
def tiling_rows(index, n, avail, win):
    import numpy as np
    rows = []
    stages = sorted({s for (s, _) in avail})
    for s in stages:
        # leftover7 = avail7 - sum n7 = 8 a ;  leftover4 = 2 b ;  leftover8 - a - 7b = 8 c
        for w, name, g in ((7, 'a', 8), (4, 'b', 2)):
            row = np.zeros(n)
            for key, j in index.items():
                if isinstance(key, tuple) and len(key) == 3 and key[0] in win and key[1] == s and key[2] == w: row[j] = 1
            row[index[(name, s)]] = g; rows.append((row, avail.get((s, w), 0), avail.get((s, w), 0)))
        row = np.zeros(n)
        for key, j in index.items():
            if isinstance(key, tuple) and len(key) == 3 and key[0] in win and key[1] == s and key[2] == 8: row[j] = 1
        row[index[('a', s)]] = 1; row[index[('b', s)]] = 7; row[index[('c', s)]] = 8
        rows.append((row, avail[(s, 8)], avail[(s, 8)]))
    return rows
def main(parent, local, out):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    g = json.loads((parent / 'GLOBAL.json').read_text()); assert hashlib.sha256(blob).hexdigest() == g['template_sha256']
    st = json.loads((local / 'records/249-states.json').read_text())
    fs = json.loads((local / 'records/frames.json').read_text())['frames']; dims = {int(f): z['dim'] for f, z in fs.items()}
    width = [H - dims[st['initial'][str(i)]] for i in range(2 * V, 2 * V + R)]
    sched = []; idx = 0
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': sched.append(dict(kind='local', stage=e['stage'], pair=e['pair']))
        elif e['kind'] == 'bridge': sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
        elif e['kind'] == 'idle': sched.append(dict(kind='idle', pair=e['pair'], rank=e['rank'], idx=idx)); e['idx'] = idx; idx += 1
    win = {k: x for k, x in TC.windows(sched).items() if x[1] > 0 and x[2]}
    avail = Counter()
    for s in range(L):
        for w in width: avail[s, w] += 1
    sel = HERE / 'SELECTION.json'; key = 'bit'
    if DISCOVER:
        counts, val = TC.solve(win, 2 * V, dict(avail), M, sorted({w for (_, w) in avail}, reverse=True), dict(vars=tiling_vars, rows=tiling_rows))
        TC.save(sel, key, counts, val)
    counts, val = TC.load(sel, key)
    helpers = {s: [(h, width[h]) for h in range(R)] for s in range(L)}
    pieces, rem = TC.expand(win, counts, helpers, 2 * V)
    left = {s: [h for h in range(R) if (s, h) not in pieces] for s in range(L)}
    nb = {}; place = {}
    for s in range(L):
        wl = {h: width[h] for h in left[s]}
        slotsS = sorted(((wl[h], rep, h) for rep in range(T) for h in left[s]), key=lambda x: (-x[0], x[1], x[2]))
        by = {}
        for w_, rep, h in slotsS: by.setdefault(w_, []).append((rep, h))
        bins = []
        def take(w_): return by[w_].pop(0)
        while by.get(7):
            cont = []; off = 0
            for _ in range(8): rep, h = take(7); cont.append((rep, h, off, 7)); off += 7
            rep, h = take(8); cont.append((rep, h, off, 8)); off += 8; assert off == 64; bins.append(cont)
        while by.get(4):
            cont = []; off = 0
            for _ in range(2): rep, h = take(4); cont.append((rep, h, off, 4)); off += 4
            for _ in range(7): rep, h = take(8); cont.append((rep, h, off, 8)); off += 8
            assert off == 64; bins.append(cont)
        while by.get(8):
            cont = []; off = 0
            for _ in range(8): rep, h = take(8); cont.append((rep, h, off, 8)); off += 8
            bins.append(cont)
        assert not any(by.values())
        nb[s] = len(bins)
        for b, cont in enumerate(bins):
            for rep, h, off, w_ in cont: place[s, rep, h] = (b, off, w_)
    base = [DATA]
    for s in range(L): base.append(base[-1] + nb[s])
    LIVE = base[-1]
    split = 0
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for h in range(R):
            if (s, h) in pieces:
                i, segs = pieces[s, h]; pair = win[i][0]
                fam = lambda cp: rep * 960 + (2 * pair + cp // V) * V + cp % V
                if len(segs) == 1:
                    cp, off, w = segs[0]; own.append([fam(cp), ['hosted', i, off, w]])
                else:
                    (c1, o1, w1), (c2, o2, w2) = segs; own.append([fam(c1), ['hosted-split', i, o1, w1, fam(c2), o2, w2]]); split += 1
            else:
                b, off, w = place[s, rep, h]; own.append([base[s] + b, ['bank', off, w]])
        assert len({(f, tuple(r)) for f, r in own}) == 2 * V + R and all(0 <= f < LIVE for f, r in own)
        c['owners'] = own
    paid = Counter()
    for c in t['calls']:
        for z in t['local_programs'][c['orientation']]:
            if z[0] == 0 and z[4]: paid[z[4]] += 1
            if z[0] == 2: paid[z[5]] += 1
    remainder = {}
    for e in t['schedule']:
        if e['kind'] == 'idle' and e['rank']:
            i = e['idx']
            if i in win:
                rr = Counter(rem[i, cp] for cp in range(2 * V)); remainder[i] = {str(k): v for k, v in sorted(rr.items())}
                for r_, n in rr.items():
                    if r_: paid[r_] += n * T
            else: paid[e['rank']] += 2 * V * T
    mass = sum(r * n for r, n in paid.items()); assert M * LIVE - mass == 2496, M * LIVE - mass
    t.update(version='compressed-nine-e8-bit-v1+idle-axis-hosting+cross-copy', live=LIVE,
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()},
                          pieces=[[s, h, i, [list(x) for x in segs]] for (s, h), (i, segs) in sorted(pieces.items())],
                          remainders=remainder, banks_per_stage=nb,
                          rule='helper (stage s, helper h) of replica r owns, on the pending idle-child projector of child i, the '
                               'coordinates [off, off+w) of data family r*960+(2*pair+side)*120+port for each piece (copy = side*120+port); '
                               'a residual has one or two pieces, on two copies of the same child; s lies strictly between the last '
                               'local/bridge touch of that pair and the child; the child keeps the remaining coordinates.'),
             helper_route='bank owner (exact width-64 tiling of the unhosted residuals of each stage) or hosted owner (one or two data families of one idle child, pending idle coordinates)')
    tb = json.dumps(t, separators=(',', ':'), sort_keys=True).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(g); res.update(status='PASS_CROSS_COPY_HOSTED_BIT_TEMPLATE', live=LIVE, physical=LIVE + 9, template_sha256=hashlib.sha256(tb).hexdigest(),
               parent_template_sha256=g['template_sha256'], profile=dict(sorted(paid.items())), paid_calls=sum(paid.values()), rank_mass=mass,
               maxchild=max(paid), banks_per_stage_hosted=nb, hosted_residuals_per_replica=len(pieces), hosted_residuals=len(pieces) * T,
               split_residuals=split, hosted_coordinates_per_replica=sum(sum(w for _, _, w in segs) for _, segs in pieces.values()),
               saved_idle_cost_proxy=val, seconds=time.monotonic() - t0)
    res['bank_assignments'] = sum(1 for c in t['calls'] for f, r in c['owners'][2 * V:] if r[0] == 'bank')
    (out / 'GLOBAL.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'split_residuals', 'banks_per_stage_hosted', 'rank_mass', 'profile')}), flush=True)
if __name__ == '__main__':
    DISCOVER = '--discover' in sys.argv; args = [a for a in sys.argv[1:] if a != '--discover']
    main(Path(args[0]), Path(args[1]), Path(args[2]))
