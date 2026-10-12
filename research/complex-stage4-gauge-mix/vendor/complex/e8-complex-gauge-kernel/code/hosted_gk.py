# GK: modified copy of PR #442's complex_hosted.py (DaysSky) by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
# Every change is marked "GK:".  At the defaults (no --selection / --key, all residual widths 9) the written files equal PR #442's.
"""Idle-axis hosting for #433's compressed nine-stage complex template (m=73, R=560, whole rank-nine residuals).
Local programs, data routes and the cover correction are unchanged; bank slots of hosted residuals move onto pending
idle-child coordinates of untouched data families; unhosted width-9 residuals are re-tiled eight per bank with one paid pad
(a final partial bank pays the larger pad); unhosted ENTERING residuals (GK) go to banks of their own, at most one per replica (hence per invocation) in a bank, with spectators in the pad.  usage: complex_hosted.py SPLIT_CENTRES_DIR OUT"""
import gzip, hashlib, json, math, sys, time
from collections import Counter, defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
PKG442 = HERE.parent.parent / 'idle-axis-hosting'   # GK: PR #442's package supplies hosting_core and the default SELECTION.json
sys.path.insert(0, str(PKG442)); sys.path.insert(0, str(HERE))
import hosting_core as HC
from gk_common import tile, widths_of, basis, route
import onehost_gk as OH
V, K, T, L, M, R = 120, 4, 8, 9, 73, 560
DATA = 2 * K * V * T
DISCOVER = False; SELECTION = None; KEY = 'complex'; DISCOVER_TO = None; ONEPER = False
def one_helper_rule(own, widths, W):
    """GK: PR #458's rule on every register class of one invocation (own = the 2V active data owners followed by the R helper owners).
    data families (f < DATA): the active families and every hosted helper (any width) are pairwise distinct;
    bank families (DATA <= f < W): an ENTERING helper (width < 9) is the only owner of its family; width-9 helpers share a pure bank as in
    PR #433 (no wrapper acts on them) and their eight 9-cell slots are disjoint;
    every other family (the private namespace, f >= W) is owned by nobody; the active owners carry route [1, ...] and are never helpers."""
    fam = Counter(f for f, r in own)
    for i, (f, r) in enumerate(own):
        helper = i >= 2 * V; w = widths[i - 2 * V] if helper else None
        if f < DATA: assert fam[f] == 1, ('two owners on one data family in one invocation', f)
        elif f < W:
            assert helper and r[0] == 2, ('a bank family owned by a non-helper', f)
            if w < L: assert fam[f] == 1, ('an entering helper shares its bank family in one invocation', f)
        else: raise AssertionError(('owner in the private namespace', f))
        assert (r[0] == 1) == (not helper)
    cells = defaultdict(set)         # disjoint footprints (residual cells and spectators) of the helpers of one bank family
    for i, (f, r) in enumerate(own):
        if i >= 2 * V and f >= DATA:
            w = widths[i - 2 * V]; foot = set(range(r[1] * L, r[1] * L + L)) if len(r) == 2 else set(range(r[1], r[1] + w)) | set(r[3])
            assert len(foot) == L and not foot & cells[f], ('footprints overlap on a bank family', f); cells[f] |= foot
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
    # GK: residual widths from the word's entrance frames (all 9 at the defaults)
    canon = json.loads(gzip.decompress((src / 'CANONICAL-WORD.json.gz').read_bytes()))
    widths = [L - len(canon['frames'][canon['start'][2 * V + i]]) for i in range(R)]
    win = {k: x for k, x in HC.windows(sched).items() if x[1] >= min(widths) and x[2]}
    avail = {}
    for w_ in widths: avail[(0, w_)] = avail.get((0, w_), 0) + 1
    avail = {(s, w_): z for s in range(L) for (_, w_), z in avail.items()}
    sel = Path(SELECTION) if SELECTION else PKG442 / 'SELECTION.json'; key = KEY
    if ONEPER:   # GK: whole residuals, at most one helper per physical family per invocation (PR #458's rule)
        OH.check_disjoint_groups(win, pair_of, side_of)
        if DISCOVER:
            psel, val = OH.solve(win, V, avail, M, HC.cost(1, M) / 8); OH.save(DISCOVER_TO or sel, key, psel, val); sel = DISCOVER_TO or sel
        psel, val = OH.load(sel, key)
        slots, rem = OH.expand(win, psel, widths, V)
        ph = json.loads(Path('work/complex-nine-native/DATA-PHASES.json').read_text())
        assert [p['q'] for p in ph['recipes']] == canon['ports'] and len(ph['recipes']) == V
    else:
        if DISCOVER:
            ys, zs, val = HC.solve(win, V, avail, M, pad_value=HC.cost(1, M) / 8); HC.save_selection(DISCOVER_TO or sel, key, ys, zs, val)
            sel = DISCOVER_TO or sel
        ys, zs, val = HC.load_selection(sel, key)
        helpers = {s: [(h, widths[h]) for h in sorted(range(R), key=lambda h: (-widths[h], h))] for s in range(L)}   # GK: widest first
        slots, rem = HC.expand(win, ys, zs, helpers, V)
    hosted = {(s, h): (i, port, off) for i, port, off, w, s, h in slots}
    # re-tile unhosted residuals: per stage, z = rank among (replica, helper) unhosted pairs; eight per bank
    base = [DATA]; tl = {}; partial = Counter()
    for s in range(L):   # GK: width-9 residuals: eight per bank and one pad, as in PR #442; entering residuals: one per replica per bank (gk_common.tile)
        left = [(rep, h, widths[h]) for rep in range(T) for h in range(R) if (s, h) not in hosted]
        asg, nb, pads = tile(left)
        for (rep, h), x_ in asg.items(): tl[s, rep, h] = x_
        base.append(base[-1] + nb); partial.update(pads)
    W = base[-1]
    for c in t['calls']:
        s, rep, p = c['stage'], c['replica'], c['pair']; own = c['owners'][:2 * V]
        for h in range(R):
            if (s, h) in hosted:
                i, port, off = hosted[s, h]; w_ = widths[h]
                if ONEPER and w_ < L:   # GK: explicit spectator chart (PR #458's route record); width 9 has no spectator and keeps [3, i, off]
                    rt = [4, i, off, w_, OH.spectators(canon['ports'][port], [int(x) for x in ph['recipes'][port]['idle_children'][i]['orthogonal_axes']], off, w_)]
                else: rt = [3, i, off]
                own.append([rep * 960 + (2 * pair_of[i] + side_of[i]) * V + port, rt])
            else:
                b, off_, w_, pure_, sp_ = tl[s, rep, h]; own.append([base[s] + b, route(off_, w_, pure_, sp_)])
        assert len({(f, json.dumps(r)) for f, r in own}) == 2 * V + R and all(f < W for f, r in own)   # every owner lies in the live stock: none in the private namespace
        if ONEPER: one_helper_rule(own, widths, W)   # GK: the rule on EVERY register class, not only the data families
        c['owners'] = own
    if ONEPER:   # GK: bank chart across all invocations: residual cells packed from 0, the spectators of an entering helper are the first cells beyond them
        occ = defaultdict(set)
        for c in t['calls']:
            for h, (f, r) in enumerate(c['owners'][2 * V:]):
                if f >= DATA: occ[f] |= set(range(r[1] * L, r[1] * L + L)) if len(r) == 2 else set(range(r[1], r[1] + widths[h]))
        for c in t['calls']:
            for h, (f, r) in enumerate(c['owners'][2 * V:]):
                if f >= DATA and widths[h] < L:
                    assert occ[f] == set(range(len(occ[f]))) and r[2] == widths[h] and r[3] == list(range(len(occ[f]), len(occ[f]) + L - widths[h])) and len(occ[f]) + L - widths[h] <= M, ('bank spectator chart', f, r)
    paid = Counter()
    for c in t['calls']:
        for r_, z in checks[c['orientation']]['paid_profile'].items(): paid[int(r_)] += z
    newidle = []
    for it in t['idle_children']:
        ch, port = it['child'], it['port']; rr = rem.get((ch, port), it['rank']) if ch in win else it['rank']
        if rr: newidle.append(dict(child=ch, port=port, rank=rr, hosted=it['rank'] - rr, replicas=T)); paid[rr] += T
    for r_, n in partial.items(): paid[r_] += L * n if False else n * 1
    # padding: one pad child per bank per stage (already per-stage counted above), the template replays all stages
    mass = sum(r * n for r, n in paid.items()); D = M * W - mass
    assert D == 2496, D
    t.update(version='hamming-mutable-basis-nine-v1+idle-axis-hosting', live=W, idle_children=newidle,
             physical=W + R + (integ['physical'] - integ['live'] - R),
             hosting=dict(windows={str(i): [w[0], w[1], sorted(w[2])] for i, w in win.items()}, sides=side_of, pairs=pair_of,
                          slots=[list(x) for x in slots], banks=[base[s + 1] - base[s] for s in range(L)]))
    if ONEPER:   # GK
        C_ = len(canon['centers']); t['private_namespace'] = {'centers': [W, W + C_], 'reserved_tableau': [W + C_, W + C_ + R], 'coefficient': [t['physical'] - 2, t['physical']]}   # re-based on the hosted stock (the parent's ranges lie beyond the hosted physical stock)
        t['hosting']['max_helpers_per_physical_family_per_call'] = 1
        t['route_semantics']['helper'] += '; entering helpers: paid wrappers R_E^-1 before and L_E^-1 after the invocation, route [4, child, offset, width, spectator indices]; an entering helper is the only owner of its physical family in the invocation (data or bank); a banked entering helper is [2, offset, width, spectator cells] with the spectators the first cells of the bank beyond every residual cell'
    t['bank_padding']['families'] = list(range(DATA, W)); t['cover_final_correction']['families'] = [0, W]
    t['cover_final_correction']['charged_calls_per_cover'] = W
    for e in t['execution_schedule']:
        if e['kind'] == 'bank_padding_cover_sweep': e['families'] = [DATA, W]
        elif e['kind'] == 'translate_every_live_family': e.update(t['cover_final_correction'])
    tb = json.dumps(t, sort_keys=True, separators=(',', ':')).encode(); (out / 'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(tb, mtime=0))
    res = dict(status='PASS_IDLE_AXIS_HOSTED_COMPLEX_TEMPLATE', parent_template_sha256=integ['global_template_sha256'],
               template_sha256=hashlib.sha256(tb).hexdigest(), live=W, physical=t['physical'], global_profile=dict(sorted(paid.items())),
               rank_mass=mass, deficit=D, maxchild=max(paid), hosted_residuals=len(slots) * T, banks_per_stage=t['hosting']['banks'],
               saved_cost_proxy=val, seconds=time.monotonic() - t0)
    (out / 'HOSTED.json').write_text(json.dumps(res, indent=2) + '\n')
    print(json.dumps({k: res[k] for k in ('live', 'maxchild', 'hosted_residuals', 'banks_per_stage', 'deficit')}))
if __name__ == '__main__':
    # GK: --selection FILE --key NAME choose a frozen selection of this package; --discover-to FILE recomputes it with scipy
    argv = sys.argv[1:]; opts = {}
    for o in ('--selection', '--key', '--discover-to'):
        if o in argv: i = argv.index(o); opts[o] = argv[i + 1]; del argv[i:i + 2]
    SELECTION = opts.get('--selection'); KEY = opts.get('--key', 'complex'); DISCOVER_TO = Path(opts['--discover-to']) if '--discover-to' in opts else None
    ONEPER = '--one-helper-per-family' in argv
    DISCOVER = '--discover' in argv or DISCOVER_TO is not None; args = [a for a in argv if a not in ('--discover', '--one-helper-per-family')]
    main(Path(args[0]), Path(args[1]))
