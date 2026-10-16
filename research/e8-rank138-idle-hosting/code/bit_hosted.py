"""Idle-axis hosting for #434's compressed nine-stage bit template (m=64).
Reads the emitted parent template, keeps every local program and scalar replay unchanged, and moves whole helper
residuals from banks onto pending idle-advance coordinates of untouched data families.  Emits a new template,
GLOBAL.json with the new live stock and paid profile.  usage: bit_hosted.py PARENT_GLOBAL_DIR LOCAL_CHECK_DIR OUT"""
import gzip, hashlib, importlib.util, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hosting_core as HC
H, V, L, K, T, M = 8, 120, 9, 4, 32, 64
DATA = 2 * K * V * T
DISCOVER = False
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(parent, local, out):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    g = json.loads((parent / 'GLOBAL.json').read_text())
    assert hashlib.sha256(blob).hexdigest() == g['template_sha256']
    st = json.loads((local / 'records/249-states.json').read_text()); R = st['n'] - 2 * V; assert R == g['R']
    fs = json.loads((local / 'records/frames.json').read_text())['frames']; dims = {int(f): z['dim'] for f, z in fs.items()}
    width = [H - dims[st['initial'][str(i)]] for i in range(2 * V, 2 * V + R)]
    # schedule with indexed idle children
    sched = []; idx = 0
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': sched.append(dict(kind='local', stage=e['stage'], pair=e['pair']))
        elif e['kind'] == 'bridge': sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
        elif e['kind'] == 'idle':
            sched.append(dict(kind='idle', pair=e['pair'], rank=e['rank'], idx=idx)); e['idx'] = idx; idx += 1
    win = {k: x for k, x in HC.windows(sched).items() if x[1] > 0 and x[2]}
    avail = Counter()
    for s in range(L):
        for w in width: avail[s, w] += 1
    sel = HERE / 'SELECTION.json'; key = 'bit'
    if DISCOVER:
        ys, zs, val = HC.solve(win, 2 * V, dict(avail), M, group={7: 2}); HC.save_selection(sel, key, ys, zs, val)
    ys, zs, val = HC.load_selection(sel, key)
    helpers = {s: [(h, width[h]) for h in range(R)] for s in range(L)}
    slots, rem = HC.expand(win, ys, zs, helpers, 2 * V)
    hosted = {(s, h): (i, c, off, w) for i, c, off, w, s, h in slots}
    # remaining helpers -> exact width-64 banks (per stage, same set of helpers in every replica)
    left = {s: [h for h in range(R) if (s, h) not in hosted] for s in range(L)}
    nb = {}; place = {}
    for s in range(L):
        wl = {h: width[h] for h in left[s]}
        slotsS = sorted(((wl[h], rep, h) for rep in range(T) for h in left[s]), key=lambda x: (-x[0], x[1], x[2]))
        by = {}
        for w_, rep, h in slotsS: by.setdefault(w_, []).append((rep, h))
        bins = []
        def take(w_): return by[w_].pop(0)
        for w_ in sorted(by, reverse=True):
            if w_ == 8: continue
            while by.get(w_):
                cont = []; off = 0
                if w_ == 7:
                    for _ in range(8): rep, h = take(7); cont.append((rep, h, off, 7)); off += 7
                    rep, h = take(8); cont.append((rep, h, off, 8)); off += 8
                else:
                    for _ in range(64 // w_): rep, h = take(w_); cont.append((rep, h, off, w_)); off += w_
                assert off == 64; bins.append(cont)
        while by.get(8):
            cont = []; off = 0
            for _ in range(8): rep, h = take(8); cont.append((rep, h, off, 8)); off += 8
            bins.append(cont)
        nb[s] = len(bins)
        for b, cont in enumerate(bins):
            for rep, h, off, w_ in cont: place[s, rep, h] = (b, off, w_)
    base = [DATA]
    for s in range(L): base.append(base[-1] + nb[s])
    LIVE = base[-1]
    # owners
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for h in range(R):
            if (s, h) in hosted:
                i, cp, off, w = hosted[s, h]; pair = win[i][0]; side, port = divmod(cp, V)
                own.append([rep * 960 + (2 * pair + side) * V + port, ['hosted', i, off, w]])
            else:
                b, off, w = place[s, rep, h]; own.append([base[s] + b, ['bank', off, w]])
        assert len({(f, tuple(r)) for f, r in own}) == 2 * V + R and all(0 <= f < LIVE for f, r in own)
        c['owners'] = own
    # profile: local programs unchanged; idle children replaced by remainders
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
            else:
                paid[e['rank']] += 2 * V * T
    mass = sum(r * n for r, n in paid.items()); assert M * LIVE - mass == 312*T, M * LIVE - mass
    t.update(version='compressed-nine-e8-bit-v1+idle-axis-hosting', live=LIVE,
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()},
                          slots=[list(x) for x in slots], remainders=remainder, banks_per_stage=nb,
                          rule='helper (stage s, helper h) of replica r owns coordinates [off, off+w) of the pending idle-child '
                               'projector of data family r*960+(2*pair+side)*120+port (copy = side*120+port); s lies strictly between '
                               'the last local/bridge touch of that pair and the child; the child keeps the remaining coordinates.'),
             helper_route='bank owner (exact width-64 tiling of the unhosted residuals of each stage) or hosted owner (data family, pending idle coordinates)')
    tb = json.dumps(t, separators=(',', ':'), sort_keys=True).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(g); res.update(status='PASS_IDLE_AXIS_HOSTED_BIT_TEMPLATE', live=LIVE, physical=LIVE + 9, template_sha256=hashlib.sha256(tb).hexdigest(),
               parent_template_sha256=g['template_sha256'], profile=dict(sorted(paid.items())), paid_calls=sum(paid.values()), rank_mass=mass,
               maxchild=max(paid), banks_per_stage_hosted=nb, hosted_residuals_per_replica=len(slots), hosted_residuals=len(slots) * T,
               hosted_coordinates_per_replica=sum(x[3] for x in slots), saved_idle_cost_proxy=val, seconds=time.monotonic() - t0)
    res['bank_assignments'] = sum(1 for c in t['calls'] for f, r in c['owners'][2 * V:] if r[0] == 'bank')
    (out / 'GLOBAL.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'banks_per_stage_hosted', 'rank_mass')}), flush=True)
if __name__ == '__main__':
    DISCOVER = '--discover' in sys.argv; args = [a for a in sys.argv[1:] if a != '--discover']
    main(Path(args[0]), Path(args[1]), Path(args[2]))
