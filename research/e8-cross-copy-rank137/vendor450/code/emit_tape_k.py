# Adapted from higherbeing PR #448 (research/cross-copy-hosting/bit_split.py; cross-copy idle-axis hosting), DaysSky PR #442
# (idle-axis hosting; Claude assistance) and chafreaky PR #444 (OpenAI Codex), Apache-2.0.
# Generalised to an arbitrary odd stage count and to host-every-residual by DreamingOfClouds with Claude Opus 5.5
# (Anthropic), via Claude Code.  At the nine-stage defaults on PR #434's bit template with PR #448's frozen selection the
# emitted GLOBAL-TEMPLATE.json.gz equals PR #448's byte for byte (GLOBAL.json except wall-clock seconds).
"""Cross-copy idle-axis hosting for a compressed S-stage bit template (m = 1+7S).  Every residual of an idle child is laid
along the concatenated pending sets of that child's 2V copies (a tape); a residual may straddle one copy boundary, in which
case its two pieces are owned by two data families of the same child (same window).  Unhosted residuals keep the exact
width-64 bank tiling of PR #442/#448 (nine stages only); with --host-all no bank remains.
usage: emit_tape_k.py PARENT_GLOBAL_DIR LOCAL_CHECK_DIR OUT --selection FILE [--key KEY] [--discover] [--host-all]
                      [--depth D] [--redigest] [--version-tag TAG]"""
import argparse, gzip, hashlib, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / 'cross-copy-hosting'))
import tape_core as TC          # PR #448, byte-identical, imported unchanged
import hosting_k as HK
H, V = 8, 120
def main(parent, local, out, a):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    g = json.loads((parent / 'GLOBAL.json').read_text()); assert hashlib.sha256(blob).hexdigest() == g['template_sha256']
    L, T, M, R = t['stages'], t['replicas'], t['m'], g['R']; K = (L - 1) // 2; DATA = 2 * K * V * T; FAM = 2 * K * V
    assert M == 1 + 7 * L and g['v'] == V and L % 2 == 1
    DEFICIT = T * (2 * K * V - 9 * H * L)
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
    sel = Path(a.selection); key = a.key
    if a.discover:
        counts, val = HK.solve_tape(win, 2 * V, dict(avail), M, host_all=a.host_all); TC.save(sel, key, counts, val)
    counts, val = TC.load(sel, key)
    helpers = {s: [(h, width[h]) for h in range(R)] for s in range(L)}
    pieces, rem = TC.expand(win, counts, helpers, 2 * V)
    if a.host_all: assert len(pieces) == L * R, 'host-all selection leaves unhosted residuals'
    left = {s: [h for h in range(R) if (s, h) not in pieces] for s in range(L)}
    nb = {}; place = {}
    if not any(left.values()):
        nb = {s: 0 for s in range(L)}
    else:
        assert M == 64, 'bank tiling is only emitted for the nine-stage layout'
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
                fam = lambda cp: rep * FAM + (2 * pair + cp // V) * V + cp % V
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
    mass = sum(r * n for r, n in paid.items()); assert M * LIVE - mass == DEFICIT, M * LIVE - mass
    t.update(version=a.version_tag, live=LIVE,
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()},
                          pieces=[[s, h, i, [list(x) for x in segs]] for (s, h), (i, segs) in sorted(pieces.items())],
                          remainders=remainder, banks_per_stage=nb,
                          rule='helper (stage s, helper h) of replica r owns, on the pending idle-child projector of child i, the '
                               'coordinates [off, off+w) of data family r*%d+(2*pair+side)*120+port for each piece (copy = side*120+port); '
                               'a residual has one or two pieces, on two copies of the same child; s lies strictly between the last '
                               'local/bridge touch of that pair and the child; the child keeps the remaining coordinates.' % FAM),
             helper_route='bank owner (exact width-%d tiling of the unhosted residuals of each stage) or hosted owner (one or two data families of one idle child, pending idle coordinates)' % M)
    if t.get('banks_per_stage') is None: t['banks_per_stage'] = nb      # bank-free parent (eleven stages); the nine-stage parent keeps PR #448's field
    tb = json.dumps(t, separators=(',', ':'), sort_keys=True).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(g); res.update(status='PASS_CROSS_COPY_HOSTED_BIT_TEMPLATE', live=LIVE, physical=LIVE + 9, template_sha256=hashlib.sha256(tb).hexdigest(),
               parent_template_sha256=g['template_sha256'], profile=dict(sorted(paid.items())), paid_calls=sum(paid.values()), rank_mass=mass,
               maxchild=max(paid), banks_per_stage_hosted=nb, hosted_residuals_per_replica=len(pieces), hosted_residuals=len(pieces) * T,
               split_residuals=split, hosted_coordinates_per_replica=sum(sum(w for _, _, w in segs) for _, segs in pieces.values()),
               saved_idle_cost_proxy=val, seconds=time.monotonic() - t0)
    res['bank_assignments'] = sum(1 for c in t['calls'] for f, r in c['owners'][2 * V:] if r[0] == 'bank')
    if a.depth is not None:
        assert 2 * max(paid) ** a.depth < M ** a.depth, ('halving depth too small', a.depth, max(paid), M)
        res['halving_depth'] = a.depth; res['halving_integer_inequality'] = [M ** a.depth, 2 * max(paid) ** a.depth]; res['deficit'] = DEFICIT
    if a.redigest:
        expanded = hashlib.sha256(); count = 0; loc = 2 * V + R
        for call in t['calls']:
            owners = call['owners']
            for z in t['local_programs'][call['orientation']]:
                op = z[0]
                if op == 0: mapped = [op, owners[z[1]], *z[2:]]
                else:
                    ox = owners[z[1]]; oy = owners[z[2]] if z[2] < loc else [LIVE, ['private', 0]]
                    mapped = [op, ox, oy, *z[3:]]
                expanded.update((json.dumps(mapped, separators=(',', ':')) + '\n').encode()); count += 1
        res['emitted_program_sha256'] = expanded.hexdigest(); res['emitted_events'] = count
    (out / 'GLOBAL.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'split_residuals', 'banks_per_stage_hosted', 'rank_mass', 'profile')}), flush=True)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('parent', type=Path); ap.add_argument('local', type=Path); ap.add_argument('out', type=Path)
    ap.add_argument('--selection', required=True); ap.add_argument('--key', default='bit'); ap.add_argument('--discover', action='store_true')
    ap.add_argument('--host-all', action='store_true'); ap.add_argument('--depth', type=int, default=None); ap.add_argument('--redigest', action='store_true')
    ap.add_argument('--version-tag', default='compressed-nine-e8-bit-v1+idle-axis-hosting+cross-copy')
    a = ap.parse_args(); main(a.parent, a.local, a.out, a)
