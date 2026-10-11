"""Cross-copy idle-axis hosting for #472's eleven-stage R715 bit template (m=78, K=5, 8 pooled replicas).
Reads #472's emitted whole-hosted template (code/emit.py output), keeps every local program, data owner, isometry
and bridge, and re-hosts every helper residual on the tape of each child's 2V*T pooled copies; a residual may be
split across two copies of the same child.  Recomputes paid profile, remainders, emitted digest and the physical
prefix bound.  usage: bit_split11.py PARENT_BIT_DIR LOCAL_DIR OUT [--discover]"""
import gzip, hashlib, json, math, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import tape_core as TC
H, V, R, L, K, T, M = 8, 120, 715, 11, 5, 8, 78
LOCAL = 2 * V + R; DATA = 2 * K * V * T; LIVE = DATA
DISCOVER = False
def digest(t):
    h = hashlib.sha256(); n = 0
    for call in t['calls']:
        own = call['owners']
        for z in t['local_programs'][call['orientation']]:
            if z[0] == 0: x = [z[0], own[z[1]], *z[2:]]
            else: x = [z[0], own[z[1]], own[z[2]] if z[2] < LOCAL else [t['live'], ['private', 0]], *z[3:]]
            h.update((json.dumps(x, separators=(',', ':')) + '\n').encode()); n += 1
    return h.hexdigest(), n
def prefix_bound(t):
    """physical-family norm growth in chronological order; a split owner updates both of its families"""
    live = t['live']; norm = [1] * live + [0]; prefix = 1
    callmap = {(c['stage'], c['replica']): c for c in t['calls']}
    fams = lambda o: [o[0]] + ([o[1][4]] if o[1][0] == 'hosted-split' else [])
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep':
            for rep in range(T):
                call = callmap[e['stage'], rep]; own = call['owners']
                for z in t['local_programs'][call['orientation']]:
                    op = z[0]
                    if op == 0: continue
                    xs = fams(own[z[1]]); ys = fams(own[z[2]]) if z[2] < LOCAL else [live]
                    if op == 1:
                        inc = abs(z[3]) * max(norm[y] for y in ys)
                        for x in xs: norm[x] += inc; prefix = max(prefix, norm[x])
                    elif op == 2: norm[live] = max(norm[x] for x in xs); prefix = max(prefix, norm[live])
                    else: norm[live] = 0
        elif e['kind'] == 'bridge':
            d, ss = e['dst'], e['src']
            for rep in range(T):
                for port in range(V):
                    for x, y in [(rep * 1200 + 2 * d * V + port, rep * 1200 + 2 * ss * V + port), (rep * 1200 + (2 * ss + 1) * V + port, rep * 1200 + (2 * d + 1) * V + port)]:
                        norm[x] += norm[y]; prefix = max(prefix, norm[x])
    assert norm[live] == 0
    return prefix
def main(parent, local, out):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    g = json.loads((parent / 'GLOBAL.json').read_text()); assert hashlib.sha256(blob).hexdigest() == g['template_sha256']
    assert g['replicas'] == T and g['R'] == R and t['m'] == M and t['stages'] == L
    st = json.loads((local / 'records/249-states.json').read_text())
    fs = json.loads((local / 'records/frames.json').read_text())['frames']; dims = {int(f): z['dim'] for f, z in fs.items()}
    width = [H - dims[st['initial'][str(i)]] for i in range(2 * V, LOCAL)]
    sched = []; idx = 0
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': sched.append(dict(kind='local', stage=e['stage'], pair=e['pair']))
        elif e['kind'] == 'bridge': sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
        elif e['kind'] == 'idle': assert e['idx'] == idx; sched.append(dict(kind='idle', pair=e['pair'], rank=e['rank'], idx=idx)); idx += 1
    win = {k: x for k, x in TC.windows(sched).items() if x[1] > 0 and x[2]}
    copies = 2 * V * T                                   # pooled: every copy of every replica is a host
    avail = Counter()
    for s in range(L):
        for rep in range(T):
            for w in width: avail[s, w] += 1
    sel = HERE / 'SELECTION.json'; key = 'bit715'
    if DISCOVER:
        counts, val = TC.solve(win, copies, dict(avail), M, sorted({w for (_, w) in avail}, reverse=True), dict(vars=lambda st: [], rows=lambda *a: []))
        TC.save(sel, key, counts, val)
    counts, val = TC.load(sel, key)
    # complete the integer programme's choice: place any residual it left out on an in-window child with room (largest ln(m/r) first)
    hostedc = Counter(); usedc = Counter()
    for (i, s, w), n in counts.items(): hostedc[s, w] += n; usedc[i] += w * n
    for (s, w), a in sorted(avail.items()):
        for _ in range(a - hostedc[s, w]):
            i = max((i for i in win if s in win[i][2] and usedc[i] + w <= win[i][1] * copies), key=lambda i: math.log(M / win[i][1]))
            counts[i, s, w] = counts.get((i, s, w), 0) + 1; usedc[i] += w
    helpers = {s: [(i, width[i % R]) for i in range(R * T)] for s in range(L)}      # helper index i = rep*R + r
    pieces, rem = TC.expand(win, counts, helpers, copies)
    assert len(pieces) == L * R * T, ('every residual must be hosted', len(pieces), L * R * T)
    split = 0
    fam = lambda i, cp: (lambda owner_rep, within: owner_rep * (2 * K * V) + (2 * win[i][0] + within // V) * V + within % V)(*divmod(cp, 2 * V))
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for r in range(R):
            i, segs = pieces[s, rep * R + r]; assert win[i][0] != p
            if len(segs) == 1:
                cp, off, w = segs[0]; own.append([fam(i, cp), ['hosted', i, off, w]])
            else:
                (c1, o1, w1), (c2, o2, w2) = segs; own.append([fam(i, c1), ['hosted-split', i, o1, w1, fam(i, c2), o2, w2]]); split += 1
        assert len({(f, tuple(rt)) for f, rt in own}) == LOCAL and all(0 <= f < LIVE for f, rt in own)
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
                rr = Counter(rem[i, cp] for cp in range(copies)); remainder[str(i)] = {str(k): v for k, v in sorted(rr.items())}
                for r_, n in rr.items():
                    if r_: paid[r_] += n
            else: paid[e['rank']] += copies
    mass = sum(r * n for r, n in paid.items()); deficit = (2 * K * V - L * 72) * T; assert M * LIVE - mass == deficit, (M * LIVE - mass, deficit)
    t.update(version=t['version'] + '+cross-copy', live=LIVE,
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()},
                          pieces=[[s, h, i, [list(x) for x in segs]] for (s, h), (i, segs) in sorted(pieces.items())], remainders=remainder,
                          rule='helper (stage s, replica-helper index h = rep*R + r) owns, on the pending idle-child projector of child i, the coordinates '
                               '[off, off+w) of pooled copy cp (owner replica cp // 240, side/port cp % 240) for each piece; one or two pieces on two copies of '
                               'the same child; s strictly inside the window; the child keeps the remaining coordinates.'),
             helper_route='hosted owner (one or two data families of one idle child, in any replica, pending idle coordinates; exact residual isometry then the slot placement)')
    prefix = prefix_bound(t); charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
    tb = json.dumps(t, separators=(',', ':'), sort_keys=True).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    dg, nev = digest(t)
    res = dict(g); res.update(status='PASS_CROSS_COPY_HOSTED_ELEVEN_STAGE_BIT_TEMPLATE', live=LIVE, physical=LIVE + 9, template_sha256=hashlib.sha256(tb).hexdigest(),
               parent_template_sha256=g['template_sha256'], profile=dict(sorted(paid.items())), paid_calls=sum(paid.values()), rank_mass=mass, deficit=deficit,
               maxchild=max(paid), halving_integer_inequality=[M ** 3, 2 * max(paid) ** 3], hosted_residuals=len(pieces), split_residuals=split,
               hosted_coordinates=sum(sum(w for _, _, w in segs) for _, segs in pieces.values()), saved_idle_cost_proxy=val,
               emitted_program_sha256=dg, emitted_events=nev, global_prefix_bound=str(prefix), global_prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix,
               seconds=time.monotonic() - t0)
    res['scope'] = res.get('scope', '') + ' Cross-copy slots (PR448) are assumed in addition; every window and coordinate ownership is audited.'
    (out / 'GLOBAL.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'split_residuals', 'rank_mass', 'profile', 'global_prefix_bits')}), flush=True)
if __name__ == '__main__':
    DISCOVER = '--discover' in sys.argv; args = [a for a in sys.argv[1:] if a != '--discover']
    main(Path(args[0]), Path(args[1]), Path(args[2]))
