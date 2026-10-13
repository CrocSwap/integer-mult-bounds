# Adapted from DaysSky PR442 (Claude assistance) and chafreaky PR444 (OpenAI Codex), Apache-2.0.
# Generalised to an arbitrary odd stage count and to host-every-residual by DreamingOfClouds with Claude Opus 5.5
# (Anthropic), via Claude Code.  At the nine-stage defaults with PR #444's frozen selection the emitted
# GLOBAL-TEMPLATE.json.gz equals PR #444's byte for byte.
"""Idle-axis hosting for a compressed S-stage bit template (m = 1+7S).
Reads the emitted parent template, keeps every local program and scalar replay unchanged, and moves whole helper
residuals from banks onto pending idle-advance coordinates of untouched data families.  Emits a new template and
GLOBAL.json with the new live stock and paid profile.
usage: emit_k.py PARENT_GLOBAL_DIR LOCAL_CHECK_DIR OUT --selection FILE --key KEY [--discover] [--host-all] [--cap N]
                 [--depth D] [--version-tag TAG]"""
import argparse, gzip, hashlib, json, sys, time
from collections import Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / 'e8-r740-replica32/code'))
from bank_routes_k import placement
import hosting_k as HK
H, V = 8, 120
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(parent, local, out, a):
    t0 = time.monotonic(); out.mkdir(parents=True, exist_ok=False)
    blob = gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()); t = json.loads(blob)
    g = json.loads((parent / 'GLOBAL.json').read_text())
    assert hashlib.sha256(blob).hexdigest() == g['template_sha256']
    L, T, M, R = t['stages'], t['replicas'], t['m'], g['R']; K = (L - 1) // 2; DATA = 2 * K * V * T
    assert M == 1 + 7 * L and g['v'] == V and L % 2 == 1
    DEFICIT = T * (2 * K * V - 9 * H * L)
    st = json.loads((local / 'records/249-states.json').read_text())
    fs = json.loads((local / 'records/frames.json').read_text())['frames']; dims = {int(f): z['dim'] for f, z in fs.items()}
    width = [H - dims[st['initial'][str(i)]] for i in range(2 * V, 2 * V + R)]
    # schedule with indexed idle children
    sched = []; idx = 0
    for e in t['schedule']:
        if e['kind'] == 'local_cover_sweep': sched.append(dict(kind='local', stage=e['stage'], pair=e['pair']))
        elif e['kind'] == 'bridge': sched.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
        elif e['kind'] == 'idle':
            sched.append(dict(kind='idle', pair=e['pair'], rank=e['rank'], idx=idx)); e['idx'] = idx; idx += 1
    win = {k: x for k, x in HK.windows(sched).items() if x[1] > 0 and x[2]}
    avail = Counter()
    for s in range(L):
        for w in width: avail[s, w] += 1
    sel = Path(a.selection); key = a.key
    if a.discover:
        group = {7: 2} if (L == 9 and not a.host_all) else None
        ys, zs, val = HK.solve(win, 2 * V, dict(avail), M, group=group, host_all=a.host_all, max_remainder=a.cap)
        HK.save_selection(sel, key, ys, zs, val)
    ys, zs, val = HK.load_selection(sel, key)
    helpers = {s: [(h, width[h]) for h in range(R)] for s in range(L)}
    slots, rem = HK.expand(win, ys, zs, helpers, 2 * V)
    hosted = {(s, h): (i, c, off, w) for i, c, off, w, s, h in slots}
    if a.host_all: assert len(hosted) == L * R, 'host-all selection leaves unhosted residuals'
    # remaining helpers -> exact width-m banks (per stage, same set of helpers in every replica)
    left = {s: [h for h in range(R) if (s, h) not in hosted] for s in range(L)}
    nb = {}; place = {}
    for s in range(L):
        original = left[s]
        if not original: nb[s] = 0; continue
        placed, nb[s] = placement([width[h] for h in original], T, M)
        for (rep, index), location in placed.items():
            place[s, rep, original[index]] = location
    base = [DATA]
    for s in range(L): base.append(base[-1] + nb[s])
    LIVE = base[-1]
    # owners
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for h in range(R):
            if (s, h) in hosted:
                i, cp, off, w = hosted[s, h]; pair = win[i][0]; side, port = divmod(cp, V)
                own.append([rep * (2 * K * V) + (2 * pair + side) * V + port, ['hosted', i, off, w]])
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
    mass = sum(r * n for r, n in paid.items()); assert M * LIVE - mass == DEFICIT, M * LIVE - mass
    D = a.depth; assert 2 * max(paid) ** D < M ** D, ('halving depth too small', D, max(paid), M)
    t.update(version=a.version_tag, live=LIVE, banks_per_stage=nb,
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()},
                          slots=[list(x) for x in slots], remainders=remainder, banks_per_stage=nb,
                          rule='helper (stage s, helper h) of replica r owns coordinates [off, off+w) of the pending idle-child '
                               'projector of data family r*%d+(2*pair+side)*120+port (copy = side*120+port); s lies strictly between '
                               'the last local/bridge touch of that pair and the child; the child keeps the remaining coordinates.' % (2 * K * V)),
             helper_route='bank owner (exact width-%d tiling of the unhosted residuals of each stage) or hosted owner (data family, pending idle coordinates)' % M)
    tb = json.dumps(t, separators=(',', ':'), sort_keys=True).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(g); res.update(status='PASS_IDLE_AXIS_HOSTED_BIT_TEMPLATE', live=LIVE, physical=LIVE + 9, template_sha256=hashlib.sha256(tb).hexdigest(),
               parent_template_sha256=g['template_sha256'], profile=dict(sorted(paid.items())), paid_calls=sum(paid.values()), rank_mass=mass,
               maxchild=max(paid), banks_per_stage=nb, banks_per_stage_hosted=nb, hosted_residuals_per_replica=len(slots), hosted_residuals=len(slots) * T,
               hosted_coordinates_per_replica=sum(x[3] for x in slots), saved_idle_cost_proxy=val, seconds=time.monotonic() - t0)
    res['bank_assignments'] = sum(1 for c in t['calls'] for f, r in c['owners'][2 * V:] if r[0] == 'bank')
    res['halving_integer_inequality'] = [M ** D, 2 * max(paid) ** D]; res['halving_depth'] = D
    res['deficit'] = DEFICIT
    res['scope'] += ' Additional PR442 idle-data hosting interface is assumed; every hosting window and coordinate ownership is audited.'
    # Re-emit the renamed stream: ownership has changed, so the parent's
    # instruction digest must not be reused.
    expanded=hashlib.sha256(); count=0; local=2*V+R
    for call in t['calls']:
        owners=call['owners']
        for z in t['local_programs'][call['orientation']]:
            op=z[0]
            if op==0: mapped=[op,owners[z[1]],*z[2:]]
            else:
                ox=owners[z[1]];oy=owners[z[2]] if z[2]<local else [LIVE,['private',0]]
                mapped=[op,ox,oy,*z[3:]]
            expanded.update((json.dumps(mapped,separators=(',',':'))+'\n').encode());count+=1
    res['emitted_program_sha256']=expanded.hexdigest();res['emitted_events']=count
    res['additional_interface']='PR442 idle-data hosting during untouched windows'
    (out / 'GLOBAL.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'banks_per_stage_hosted', 'rank_mass')}), flush=True)
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('parent', type=Path); ap.add_argument('local', type=Path); ap.add_argument('out', type=Path)
    ap.add_argument('--selection', required=True); ap.add_argument('--key', default='bit'); ap.add_argument('--discover', action='store_true')
    ap.add_argument('--host-all', action='store_true'); ap.add_argument('--cap', type=int, default=None)
    ap.add_argument('--depth', type=int, default=2); ap.add_argument('--version-tag', default='r740-replicated-idle-hosting-v1')
    a = ap.parse_args(); main(a.parent, a.local, a.out, a)
