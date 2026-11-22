#!/usr/bin/env python3
"""fill17.py -- lane C's fill.py (r12) adapted to PR #2917's words: literal owner allocation for #2917's exact
per-provider widths (allocation/PROVIDERS.json) under a chosen chronology, with the integer pattern mix of relax.py,
CP-SAT (single thread), edge-colouring realization, the vendored PR2839 owner engine (sha 77a84872..., the same file
#2917 ships in allocation/vendor/) and root.py's exact bracket.  Also replays/prices any literal fill (--check-fill).

Chronologies:
  pr2833-t37 : PR2833 T37 owners chronology (333 calls) as used by PR2857/lane C (template/plan from PR2857 sources)
  pr2833-t74 : PR2833 borrow-fill chronology (666 calls)
  pr2917-t74 : #2917's own allocation/ORDER.json + DISPATCH.json (666 calls; = PR2908's, 'inherited chronology')
Template and plan payloads are byte-identical across the packages (decompressed sha 514e5931..., 163431bf...).

Usage (AGI venv = OR-Tools 9.15; num_search_workers MUST be 1 on this machine):
  $AGI -B fill17.py --work OUT/x --chronology pr2833-t37 --catalogue tight --hint-flow PR2857/FLOW.json.gz --hint-zeros --seed 7 --seconds 900
  $AGI -B fill17.py --work OUT/x --chronology pr2917-t74 --catalogue tight --hint-fill PR2917/allocation/FILL.json.gz --hint-zeros
  $AGI -B fill17.py --work OUT/x --chronology pr2917-t74 --check-fill PR2917/allocation/FILL.json.gz   (replay + price)
  --mix-only : stop after the pattern mix and its exact kappa (fill-independent)
  --mix-file PATTERNS.json : use a given target mix (list of [cap, counts, n]) instead of the milp
Outputs: PATTERNS.json, MODEL.json, SOLVER.json, FLOW.json.gz, ORDER.json, FILL.json.gz, DISPATCH.json, PROFILE.json,
  PROVIDERS.json (= #2917's allocation format), OWNER-CHECK.json (engine result, physical stock, exact bracket, cap, gains).
"""
import os, sys
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
import argparse, collections, gzip, hashlib, json, pathlib, time, types
from fractions import Fraction as Q
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import root as R
import relax as X

SCR = pathlib.Path('S')
PKG17 = SCR / 'r13/vendor/pr2917/research/paired-helper-extension'
PKG57 = SCR / 'r12/vendor/pr2857/research/shared-kernel-repacking'
P33 = SCR / 'r12/vendor/pr2833/research/gmx-t74-borrow43-handoff'
ENGINE = PKG17 / 'allocation/vendor/independent_owners.py'
ENGINE_SHA = '77a848729159e271ba64f403dfd59dddb13044b17b2950fa56700f442e2fe461'
PR2917_KAPPA = Q('17215886471978018806049999999999999999999998999999999999999999999999/10000000000000000000000000000000000000000000000000000000000000000000000')
PR2917_ROOT_LOWER = Q('1721588647197801880605/1000000000000000000000000')   # floor of its root at 24 digits (CLAIM complex_lower = 344317729439560376121/2e23)
PRIVATE_BUFFERS = 82   # default; --buffers overrides (n45x4 words: 86)
PR2930_KAPPA = Q(17224999064432745643569999999999999999999998999999999999999999999999, 10 ** 70)   # PR2930 CLAIM (= our PR2917 cap fill)
PR2966_HEAD24 = Q(1724034272523452177412, 10 ** 24)   # #2966 headline at 24 digits (coordinator: 0.001724034272523452177412; its -1e-46-1e-70 cancels against ours)
HELPERS = 408
CENTRES = 8
GUARDS = 2


def read(p):
    b = pathlib.Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def save(p, x):
    b = json.dumps(x, sort_keys=True, separators=(',', ':')).encode()
    if str(p).endswith('.gz'):
        b = bytearray(gzip.compress(b, mtime=0))
        b[9] = 255
        b = bytes(b)
    pathlib.Path(p).write_bytes(b)


def log(*a):
    print(*a, flush=True)


def load_chronology(name):
    if name == 'pr2833-t37':
        template = read(PKG57 / 'sources/PR2833-T37-TEMPLATE.json.gz')
        plan = read(PKG57 / 'sources/PR2833-PLAN.json.gz')
        owners = read(PKG57 / 'sources/PR2833-T37-OWNERS.json.gz')
        T = 37
        timecalls = {}
        for r in owners:
            key, call = r['time'], (r['stage'], r['replica'])
            assert key not in timecalls or timecalls[key] == call
            timecalls[key] = call
        assert set(timecalls) == set(range(9 * T))
        order = [list(timecalls[t]) for t in range(9 * T)]
        dispatch = read(PKG57 / 'sources/PR2833-T37-DISPATCH.json')
    elif name == 'pr2833-t74':
        template = read(PKG57 / 'sources/PR2833-T37-TEMPLATE.json.gz')
        plan = read(PKG57 / 'sources/PR2833-PLAN.json.gz')
        order = read(P33 / 'new/borrow-fill/ORDER.json')
        dispatch = read(P33 / 'new/borrow-fill/DISPATCH.json')
        T = 74
    elif name == 'pr2917-t74':
        template = read(PKG17 / 'allocation/vendor/TEMPLATE.json.gz')
        plan = read(PKG17 / 'allocation/vendor/PLAN.json.gz')
        order = read(PKG17 / 'allocation/ORDER.json')
        dispatch = read(PKG17 / 'allocation/DISPATCH.json')
        T = 74
    else:
        raise SystemExit('unknown chronology ' + name)
    assert {(s, r) for s, r, p in dispatch} == set(map(tuple, order)) and len(order) == 9 * T and len(dispatch) == 9 * T
    return template, plan, order, dispatch, T


def load_providers(path, local_override=None):
    providers = read(path)
    out = {}
    for pid, v in providers.items():
        widths = [int(w) for w in v['widths']]
        assert len(widths) == HELPERS
        local = {int(k): int(n) for k, n in v['actual_paid_profile'].items()}
        if local_override is not None:
            local = dict(local_override)
        local = {k: n for k, n in sorted(local.items()) if n}
        assert sum(r * n for r, n in local.items()) - sum(widths) == 1856, 'local mass - width mass != 1856 for ' + pid
        out[pid] = {'widths': widths, 'actual_paid_profile': local}
    return out


def integer_pattern_mix(inv_by_call, T, bins_per_replica, cap_root, catalogue, tight):
    widths = sorted({w for inv in inv_by_call for w in inv})
    bins = {c: n * T for c, n in bins_per_replica.items()}
    demand = collections.Counter()
    for inv in inv_by_call:
        for w, n in inv.items():
            demand[w] += n
    from scipy.optimize import milp, Bounds, LinearConstraint
    pats = X.patterns(bins_per_replica, widths)
    if catalogue == 'tight':
        keep = {(t['capacity'], tuple(t['widths'].count(w) for w in widths)) for t in tight}
        for cap in bins:
            for i, w in enumerate(widths):
                if w <= cap:
                    keep.add((cap, tuple(int(j == i) for j in range(len(widths)))))
            keep.add((cap, tuple(0 for _ in widths)))
        pats = [p for p in pats if (p[0], p[1]) in keep]
    elif catalogue == 'tightonly':
        keep = {(t['capacity'], tuple(t['widths'].count(w) for w in widths)) for t in tight}
        pats = [p for p in pats if (p[0], p[1]) in keep]
    caps = sorted(bins)
    b = float(cap_root)
    c = np.array([X.Hfloat(r, b) for cap, counts, r in pats])
    A = np.zeros((len(caps) + len(widths), len(pats)))
    for j, (cap, counts, r) in enumerate(pats):
        A[caps.index(cap), j] = 1.0
        for i, n in enumerate(counts):
            A[len(caps) + i, j] = n
    rhs = np.array([float(bins[cap]) for cap in caps] + [float(demand[w]) for w in widths])
    res = milp(c, integrality=np.ones(len(pats)), bounds=Bounds(0, np.inf), constraints=LinearConstraint(A, rhs, rhs), options={'time_limit': 120, 'mip_rel_gap': 0})
    assert res.x is not None, 'integer pattern mix infeasible: ' + str(res.message)
    xi = np.rint(res.x).astype(np.int64)
    assert np.max(np.abs(xi - res.x)) < 1e-6 and np.all(A @ xi == rhs)
    target = {(pats[j][0], pats[j][1]): int(xi[j]) for j in range(len(pats)) if xi[j]}
    return target, widths


def color_pattern(n, q, counts, WID):
    slots = [w for j, w in enumerate(WID) for _ in range(q[j])]
    if not slots:
        assert not counts
        return [[] for _ in range(n)]
    times = sorted({t for t, w in counts})
    K = len(times)
    assert K >= len(slots)
    ti = {t: j for j, t in enumerate(times)}
    A = np.zeros((K, K), dtype=np.int64)
    slot_by_w = collections.defaultdict(list)
    for j, w in enumerate(slots):
        slot_by_w[w].append(j)
    for w, js in slot_by_w.items():
        atslot = 0
        remaining = n
        for t in times:
            needed = counts.get((t, w), 0)
            while needed:
                take = min(needed, remaining)
                A[ti[t], js[atslot]] += take
                needed -= take
                remaining -= take
                if remaining == 0:
                    atslot += 1
                    remaining = n
        assert atslot == len(js)
    assert all(v <= n for v in A.sum(axis=1))
    j = len(slots)
    remaining = n
    for r in range(K):
        needed = n - int(A[r].sum())
        while needed:
            assert j < K
            take = min(needed, remaining)
            A[r, j] += take
            needed -= take
            remaining -= take
            if remaining == 0:
                j += 1
                remaining = n
    assert np.all(A.sum(axis=0) == n) and np.all(A.sum(axis=1) == n)
    output = []
    for color in range(n):
        matching = maximum_bipartite_matching(csr_matrix(A > 0), perm_type='column')
        assert len(matching) == K and min(matching) >= 0 and len(set(map(int, matching))) == K
        output.append([(times[r], slots[int(c)]) for r, c in enumerate(matching) if c < len(slots)])
        A[np.arange(K), matching] -= 1
    assert not A.any()
    return output


def pattern_name(WID, counts):
    return '+'.join(str(w) for w, k in zip(WID, counts) for _ in range(k)) or 'empty'


def fill_to_bins(fill, order, disp, providers):
    """literal fill rows -> {bin: [(t, w)]} using the provider widths (helper column = 0-based index, as the engine reads it)."""
    bybin = collections.defaultdict(list)
    for t, h, o, c, p, z in fill['rows']:
        w = providers[disp[tuple(order[t])]]['widths'][h]
        bybin[o, c, p].append((t, w))
    return bybin


def price(profile, T, rel):
    k_lo, k_hi = R.kappa_from_profile(profile, T)
    cap_hi = Q(rel['cap_upper'])
    return k_lo, k_hi, dict(kappa_lower=str(k_lo), kappa_upper=str(k_hi), kappa_lower_decimal=R.mpmath_str(k_lo, 25), kappa_upper_decimal=R.mpmath_str(k_hi, 25),
                            headline_floor24_minus=str(Q(int(k_lo * 10 ** 24), 10 ** 24) - Q(1, 10 ** 46) - Q(1, 10 ** 70)),
                            relaxation_cap_lower=rel['cap_lower'], relaxation_cap_upper=rel['cap_upper'], relaxation_cap_upper_decimal=rel['cap_upper_decimal'],
                            gap_to_relaxation_cap=float(cap_hi - k_lo), gain_vs_PR2917_claim_float=float(k_lo - PR2917_KAPPA), gain_vs_PR2917_root_lower_float=float(k_lo - PR2917_ROOT_LOWER),
                            gain_vs_PR2917_claim_exact_lower=str(k_lo - PR2917_KAPPA),
                            gain_vs_PR2930_claim_float=float(k_lo - PR2930_KAPPA), gain_vs_PR2930_claim_exact_lower=str(k_lo - PR2930_KAPPA),
                            gain_vs_PR2966_headline24=str(Q(int(k_lo * 10 ** 24), 10 ** 24) - PR2966_HEAD24), gain_vs_PR2966_float=float(Q(int(k_lo * 10 ** 24), 10 ** 24) - PR2966_HEAD24))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--work', type=pathlib.Path, required=True)
    ap.add_argument('--chronology', choices=['pr2833-t37', 'pr2833-t74', 'pr2917-t74'], default='pr2833-t37')
    ap.add_argument('--providers', type=pathlib.Path, default=PKG17 / 'allocation/PROVIDERS.json')
    ap.add_argument('--local', help='JSON per-call local profile overriding PROVIDERS (both providers)')
    ap.add_argument('--catalogue', default='tight', help="all | tight | tightonly | rc:<x> (free-mix: patterns with reduced cost <= x at the cap root)")
    ap.add_argument('--mix-file', type=pathlib.Path, help='PATTERNS.json-style target list [[cap, counts, n], ...] to use instead of the milp')
    ap.add_argument('--mix-only', action='store_true')
    ap.add_argument('--seconds', type=int, default=600)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--seed', type=int, default=124)
    ap.add_argument('--hint-flow', type=pathlib.Path, help='FLOW.json.gz of the same chronology/T (e.g. PR2857 allocation/construction/FLOW.json.gz for pr2833-t37)')
    ap.add_argument('--hint-fill', type=pathlib.Path, help='literal FILL.json.gz of the same chronology (e.g. #2917 allocation/FILL.json.gz for pr2917-t74); converted to X/Z hints')
    ap.add_argument('--hint-zeros', action='store_true')
    ap.add_argument('--reuse-flow', type=pathlib.Path)
    ap.add_argument('--solver', choices=['cp', 'highs-lp', 'highs-mip'], default='cp', help='cp = CP-SAT; highs-lp = LP relaxation feasibility only (fractional flow); highs-mip = scipy milp')
    ap.add_argument('--check-fill', type=pathlib.Path, help='replay: owner-check and price this literal fill under the chronology (no solve)')
    ap.add_argument('--free-mix', action='store_true', help='no global pattern targets: CP-SAT minimizes the linearized moment sum_bins H_idle(b*) over the catalogue (tight = relaxation-tight + single residues + empties; all = every pattern; rc:x = reduced cost <= x)')
    ap.add_argument('--objective-scale', type=int, default=10 ** 6)
    ap.add_argument('--buffers', type=int, default=PRIVATE_BUFFERS, help='private zero buffers for the physical display (PR2917 82, n45x4 86)')
    ap.add_argument('--method', default='r13 lane C1: relax.py integer pattern mix + CP-SAT chronological flow + edge-colouring realization (fill17.py)')
    a = ap.parse_args()
    assert a.workers == 1, 'num_search_workers must be 1 on this machine (3 deadlocks)'
    out = a.work.resolve()
    out.mkdir(parents=True, exist_ok=False)
    t0 = time.time()
    assert hashlib.sha256(ENGINE.read_bytes()).hexdigest() == ENGINE_SHA, 'owner engine pin'
    owner = types.ModuleType('frozen_owner')
    exec(compile(ENGINE.read_bytes(), 'frozen_owner', 'exec'), owner.__dict__)
    template, plan, order, dispatch, T = load_chronology(a.chronology)
    local_override = {int(k): int(v) for k, v in json.loads(a.local).items()} if a.local else None
    providers = load_providers(a.providers, local_override)
    disp = {(s, r): p for s, r, p in dispatch}
    inv_by_call = [collections.Counter(providers[disp[tuple(sr)]]['widths']) for sr in order]
    calls_by_pid = collections.Counter(disp[tuple(sr)] for sr in order)
    locals_ = {pid: providers[pid]['actual_paid_profile'] for pid in providers}
    # relaxation cap (call-weighted average inventory; the local profile is the same for both providers here)
    avg_inv = collections.Counter()
    for inv in inv_by_call:
        for w, n in inv.items():
            avg_inv[w] += Q(n, len(order))
    loc0 = next(iter(locals_.values()))
    assert all(l == loc0 for l in locals_.values()), 'providers differ in local profile; relax.py needs one profile'
    rel = X.relax(loc0, avg_inv)
    cap_lo, cap_hi = Q(rel['cap_lower']), Q(rel['cap_upper'])
    log('CHRONOLOGY', a.chronology, 'T', T, 'calls', len(order), 'calls per provider', dict(calls_by_pid))
    log('INVENTORY', {pid: dict(sorted(collections.Counter(providers[pid]['widths']).items())) for pid in providers}, 'LOCAL', loc0)
    log('RELAX cap', rel['cap_lower_decimal'], rel['cap_upper_decimal'], 'tight', rel['tight_patterns'], 'idle/replica', rel['idle_per_replica'])
    live = 896 * T
    physical = live + HELPERS + CENTRES + a.buffers + GUARDS

    if a.check_fill:
        fill = read(a.check_fill)
        result, _, _ = owner.check(T, order, fill, disp, None, plan, template, providers)
        profile = {int(k): v for k, v in result['profile'].items()}
        k_lo, k_hi, pr = price(profile, T, rel)
        bybin = fill_to_bins(fill, order, disp, providers)
        pat_hist = collections.Counter()
        win = owner.windows(template, order, T)
        for (o, c), (cap, lo, hi) in win.items():
            for port in range(112):
                rs = bybin.get((o, c, port), [])
                pat_hist['%d:%s' % (cap, '+'.join(str(w) for w in sorted(w for t, w in rs)) or 'empty')] += 1
        assert result['live'] == live
        check = dict(result, status='PASS_VENDORED_PR2839_OWNER_ENGINE_CHECK', mode='check-fill', fill=str(a.check_fill), chronology=a.chronology, T=T,
                     physical=result['live'] + HELPERS + CENTRES + a.buffers + GUARDS, physical_expected=physical, pattern_histogram=dict(sorted(pat_hist.items())), **pr)
        save(out / 'OWNER-CHECK.json', check)
        save(out / 'PROFILE.json', dict(sorted(profile.items())))
        log('CHECK-FILL PASS roles', result['roles'], 'idle', result['idle'], 'physical', check['physical'])
        log('PATTERNS', dict(sorted(pat_hist.items())))
        log('KAPPA', pr['kappa_lower_decimal'], '..', pr['kappa_upper_decimal'], 'cap', rel['cap_upper_decimal'], 'gap %.3e' % pr['gap_to_relaxation_cap'], 'gain vs PR2917 claim %.4e' % pr['gain_vs_PR2917_claim_float'], 'gain vs PR2930 claim %.4e' % pr['gain_vs_PR2930_claim_float'], 'gain vs PR2966 %.6e' % pr['gain_vs_PR2966_float'])
        return

    bins_per_replica = X.BINS
    if a.free_mix:
        WIDf = sorted({w for inv in inv_by_call for w in inv})
        allp = X.patterns(bins_per_replica, WIDf)
        bstar = float((cap_lo + cap_hi) / 2)
        if a.catalogue.startswith('rc:'):
            thr = float(a.catalogue.split(':')[1])
            Y = rel['dual_Y']
            yv = lambda row: sum(float(Q(v)) * X.Hfloat(int(k), bstar) for k, v in Y[row].items())
            keep = {(cap, counts) for cap, counts, r in allp if X.Hfloat(r, bstar) - yv('cap%d' % cap) - sum(n * yv('w%d' % w) for w, n in zip(WIDf, counts)) <= thr}
        elif a.catalogue == 'all':
            keep = {(cap, counts) for cap, counts, r in allp}
        else:
            keep = {(t['capacity'], tuple(t['widths'].count(w) for w in WIDf)) for t in rel['tight_pattern_list']}
            for cap in bins_per_replica:
                for i, w in enumerate(WIDf):
                    if w <= cap:
                        keep.add((cap, tuple(int(j == i) for j in range(len(WIDf)))))
                keep.add((cap, tuple(0 for _ in WIDf)))
        target = {k: None for k in sorted(keep)}
        WID = WIDf
        log('FREE MIX catalogue', {cap: sum(1 for c, q in keep if c == cap) for cap in sorted(bins_per_replica)})
    elif a.mix_file:
        mf = read(a.mix_file)
        WID = [int(w) for w in mf['widths']]
        target = {(int(cap), tuple(int(k) for k in counts)): int(n) for cap, counts, n in mf['target']}
    else:
        target, WID = integer_pattern_mix(inv_by_call, T, bins_per_replica, (cap_lo + cap_hi) / 2, a.catalogue, rel['tight_pattern_list'])
    idle_mix = collections.Counter()
    for (cap, counts), n in target.items():
        r = cap - sum(w * k for w, k in zip(WID, counts))
        assert r >= 0
        if r and n:
            idle_mix[r] += n
    profile_mix = collections.Counter(idle_mix)
    for pid, ncalls in calls_by_pid.items():
        for r, n in locals_[pid].items():
            profile_mix[r] += n * ncalls
    if a.free_mix:
        mix_lo = mix_hi = None
        mix_pr = dict(kappa_lower_decimal='(free mix)', kappa_upper_decimal='', gap_to_relaxation_cap=float('nan'), gain_vs_PR2917_claim_float=float('nan'), gain_vs_PR2930_claim_float=float('nan'))
    else:
        mix_lo, mix_hi, mix_pr = price(dict(profile_mix), T, rel)
    if not a.free_mix:
        log('PATTERN MIX', {('%d:%s' % (cap, pattern_name(WID, counts))): n for (cap, counts), n in sorted(target.items())})
    log('MIX kappa bracket', mix_pr['kappa_lower_decimal'], mix_pr['kappa_upper_decimal'], 'idle', dict(sorted(idle_mix.items())), 'gap to cap %.3e' % mix_pr['gap_to_relaxation_cap'], 'gain vs PR2917 %.4e' % mix_pr['gain_vs_PR2917_claim_float'], 'gain vs PR2930 %.4e' % mix_pr['gain_vs_PR2930_claim_float'])
    if not a.free_mix:
      save(out / 'PATTERNS.json', dict(mode='milp' if not a.mix_file else 'file', catalogue=a.catalogue, T=T, chronology=a.chronology, widths=WID,
                                     target=[[cap, list(counts), n] for (cap, counts), n in sorted(target.items())], idle=dict(sorted(idle_mix.items())),
                                     profile=dict(sorted(profile_mix.items())), **mix_pr))
    if a.mix_only:
        return

    # ---- chronology windows and the flow model (PR2857 discover_original.py, all bins active)
    win = owner.windows(template, order, T)
    family = lambda b: b[0] * 896 + (2 * plan['pairs'][str(b[1])] + plan['sides'][str(b[1])]) * 112 + b[2]
    fw = collections.defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        fw[family((o, c, 0))].append((lo, hi, c))
    for ww in fw.values():
        for i, (lo, hi, c) in enumerate(ww):
            assert all(max(lo, l) >= min(hi, h) for l, h, d in ww[i + 1:]), 'overlapping same-family windows'
    need = {t: collections.Counter(inv_by_call[t]) for t in range(len(order))}
    pats = collections.defaultdict(list)
    for (cap, counts) in target:
        pats[cap].append(counts)
    groups = collections.defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        for port in range(112):
            groups[cap, tuple(range(max(0, lo + 1), min(len(order), hi + 1)))].append((o, c, port))
    G = sorted(groups)
    groupof = {b: gi for gi, g in enumerate(G) for b in groups[g]}
    edge, lb, ub, rl, ru = [], [], [], [], []
    Xv, Zv = {}, {}

    def cr(l, u=None):
        j = len(rl)
        rl.append(l)
        ru.append(l if u is None else u)
        return j

    def cv(u):
        j = len(lb)
        lb.append(0)
        ub.append(u)
        return j

    def put(r, v, n):
        if n:
            edge.append((r, v, n))
    callrow = {(t, w): cr(n) for t, cnt in need.items() for w, n in cnt.items() if n}
    globalrow = {} if a.free_mix else {key: cr(n) for key, n in target.items()}
    for gi, (cap, ts) in enumerate(G):
        nb = len(groups[G[gi]])
        br = cr(nb)
        for q in pats[cap]:
            xv = cv(nb)
            Xv[gi, q] = xv
            put(br, xv, 1)
            if not a.free_mix:
                put(globalrow[cap, q], xv, 1)
            residual = {w: q[j] for j, w in enumerate(WID) if q[j]}
            wr = {w: cr(0) for w in residual}
            for w, n in residual.items():
                put(wr[w], xv, -n)
            for t in ts:
                tr = cr(-nb, 0)
                put(tr, xv, -1)
                for w in residual:
                    if (t, w) not in callrow:
                        continue
                    zv = cv(min(nb, need[t][w]))
                    Zv[gi, q, t, w] = zv
                    put(tr, zv, 1)
                    put(wr[w], zv, 1)
                    put(callrow[t, w], zv, 1)
    modelinfo = dict(T=T, chronology=a.chronology, groups=len(G), variables=len(lb), pattern_variables=len(Xv), flow_variables=len(Zv), constraints=len(rl), nonzeros=len(edge), workers=a.workers,
                     catalogue=a.catalogue, patterns_per_cap={str(cap): len(ps) for cap, ps in pats.items()})
    save(out / 'MODEL.json', modelinfo)
    log('MODEL', modelinfo)
    rr = np.fromiter((e[0] for e in edge), np.int32)
    cc = np.fromiter((e[1] for e in edge), np.int32)
    vv = np.fromiter((e[2] for e in edge), np.float64)
    mat = coo_matrix((vv, (rr, cc)), shape=(len(rl), len(lb))).tocsr()
    del edge
    t1 = time.time()
    if a.reuse_flow:
        saved = read(a.reuse_flow)
        value = np.zeros(len(lb), dtype=np.int64)
        for gi, q, n in saved['x']:
            value[Xv[gi, tuple(q)]] = n
        for gi, q, t, w, n in saved['z']:
            value[Zv[gi, tuple(q), t, w]] = n
        status = 'EXACT_FLOW_REPLAY'
    elif a.solver == 'highs-lp':
        from scipy.optimize import milp, Bounds, LinearConstraint
        r = milp(np.zeros(len(lb)), integrality=np.zeros(len(lb)), bounds=Bounds(np.array(lb, dtype=float), np.array(ub, dtype=float)), constraints=LinearConstraint(mat, np.array(rl, dtype=float), np.array(ru, dtype=float)), options={'time_limit': a.seconds, 'disp': True})
        status = 'LP_RELAXATION_' + ('FEASIBLE' if r.x is not None else 'INFEASIBLE_OR_FAILED') + ': ' + str(r.message)
        log('LP RELAXATION', status, '%.1f s' % (time.time() - t1))
        save(out / 'SOLVER.json', dict(status=status, solver='highs-lp', seconds=time.time() - t1, chronology=a.chronology, T=T, catalogue=a.catalogue, mix_file=str(a.mix_file) if a.mix_file else None))
        return
    elif a.solver == 'highs-mip':
        from scipy.optimize import milp, Bounds, LinearConstraint
        r = milp(np.zeros(len(lb)), integrality=np.ones(len(lb)), bounds=Bounds(np.array(lb, dtype=float), np.array(ub, dtype=float)), constraints=LinearConstraint(mat, np.array(rl, dtype=float), np.array(ru, dtype=float)), options={'time_limit': a.seconds, 'mip_rel_gap': 0, 'disp': True})
        status = str(r.message)
        value = None if r.x is None else np.rint(r.x).astype(np.int64)
    else:
        from ortools.sat.python import cp_model
        model = cp_model.CpModel()
        vs = [model.NewIntVar(int(l), int(u), '') for l, u in zip(lb, ub)]
        for j, (l, u) in enumerate(zip(rl, ru)):
            b, e = mat.indptr[j:j + 2]
            ind = mat.indices[b:e]
            co = mat.data[b:e]
            model.AddLinearConstraint(cp_model.LinearExpr.WeightedSum([vs[int(k)] for k in ind], [int(k) for k in co]), int(l), int(u))
        if a.free_mix:
            bstar = float((cap_lo + cap_hi) / 2)
            obj = []
            for (gi, q), j in Xv.items():
                r = G[gi][0] - sum(w * k for w, k in zip(WID, q))
                c = 0 if r == 0 else int(round(a.objective_scale * X.Hfloat(r, bstar)))
                if c:
                    obj.append((vs[j], c))
            model.Minimize(cp_model.LinearExpr.WeightedSum([v for v, c in obj], [c for v, c in obj]))
        hinted = {}
        if a.hint_flow:
            saved = read(a.hint_flow)
            for gi, q, n in saved['x']:
                if (gi, tuple(q)) in Xv:
                    hinted[Xv[gi, tuple(q)]] = min(int(n), int(ub[Xv[gi, tuple(q)]]))
            for gi, q, t, w, n in saved['z']:
                if (gi, tuple(q), t, w) in Zv:
                    hinted[Zv[gi, tuple(q), t, w]] = min(int(n), int(ub[Zv[gi, tuple(q), t, w]]))
            log('HINT from flow', a.hint_flow, 'variables', len(hinted), 'of', len(vs))
        if a.hint_fill:
            hf = read(a.hint_fill)
            bybin = fill_to_bins(hf, order, disp, providers)
            hx = collections.Counter()
            hz = collections.Counter()
            missing = collections.Counter()
            for gi_, g_ in enumerate(G):
                for b in groups[g_]:
                    rs = bybin.get(b, [])
                    q = tuple(sum(1 for t, w in rs if w == ww) for ww in WID)
                    if (gi_, q) not in Xv:
                        missing['%d:%s' % (G[gi_][0], pattern_name(WID, q))] += 1
                        continue
                    hx[gi_, q] += 1
                    for t, w in rs:
                        hz[gi_, q, t, w] += 1
            for k, n in hx.items():
                hinted[Xv[k]] = min(n, int(ub[Xv[k]]))
            for k, n in hz.items():
                if k in Zv:
                    hinted[Zv[k]] = min(n, int(ub[Zv[k]]))
            log('HINT from fill', a.hint_fill, 'bins hinted', sum(hx.values()), 'bins with non-catalogue patterns (unhinted)', sum(missing.values()), dict(missing.most_common(12)), 'variables', len(hinted))
        if hinted:
            for j, v in hinted.items():
                model.AddHint(vs[j], v)
            if a.hint_zeros:
                for j in range(len(vs)):
                    if j not in hinted:
                        model.AddHint(vs[j], 0)
            log('HINT total', len(hinted), '(+ zeros for the rest)' if a.hint_zeros else '')
        solver = cp_model.CpSolver()
        solver.parameters.num_search_workers = a.workers
        solver.parameters.max_time_in_seconds = a.seconds
        solver.parameters.random_seed = a.seed
        solver.parameters.log_search_progress = True
        result = solver.Solve(model)
        status = solver.StatusName(result)
        value = np.array([solver.Value(v) for v in vs], dtype=np.int64) if result in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None
        log(solver.ResponseStats())
    solve_seconds = time.time() - t1
    log('SOLVER', status, '%.1f s' % solve_seconds)
    save(out / 'SOLVER.json', dict(status=status, seconds=solve_seconds, workers=a.workers, seed=a.seed, max_time_seconds=a.seconds, candidate=value is not None, chronology=a.chronology, T=T, catalogue=a.catalogue,
                                   hint_flow=str(a.hint_flow) if a.hint_flow else None, hint_fill=str(a.hint_fill) if a.hint_fill else None, hint_zeros=a.hint_zeros))
    if value is None:
        log('NO FEASIBLE FLOW (status %s)' % status)
        raise SystemExit(2)
    assert not (np.any(value < lb) or np.any(value > ub) or np.any(mat @ value < rl) or np.any(mat @ value > ru))
    xc = collections.defaultdict(collections.Counter)
    zc = collections.defaultdict(collections.Counter)
    for (gi, q), v in Xv.items():
        if value[v]:
            xc[gi][q] = int(value[v])
    for (gi, q, t, w), v in Zv.items():
        if value[v]:
            zc[gi, q][t, w] = int(value[v])
    save(out / 'FLOW.json.gz', {'x': [[gi, list(q), n] for gi, c in xc.items() for q, n in c.items()], 'z': [[gi, list(q), t, w, n] for (gi, q), c in zc.items() for (t, w), n in c.items()]})
    gc = collections.Counter()
    for gi, c in xc.items():
        for q, n in c.items():
            gc[G[gi][0], q] += n
    if a.free_mix:
        target = dict(gc)
        idle_mix = collections.Counter()
        for (cap, counts), n in target.items():
            r = cap - sum(w * k for w, k in zip(WID, counts))
            if r:
                idle_mix[r] += n
        profile_mix = collections.Counter(idle_mix)
        for pid, ncalls in calls_by_pid.items():
            for r, n in locals_[pid].items():
                profile_mix[r] += n * ncalls
        log('FREE MIX realized', {('%d:%s' % (cap, pattern_name(WID, counts))): n for (cap, counts), n in sorted(target.items())})
    assert dict(gc) == target, 'global integer pattern counts differ'
    for gi in range(len(G)):
        assert sum(xc[gi].values()) == len(groups[G[gi]]), 'window class bin count'
    call_count = collections.defaultdict(collections.Counter)
    for (gi, q), c in zc.items():
        by_w = collections.Counter()
        by_t = collections.Counter()
        for (t, w), n in c.items():
            assert t in G[gi][1] and q[WID.index(w)] > 0, 'ineligible time/width flow'
            by_w[w] += n
            by_t[t] += n
            call_count[t][w] += n
        assert all(by_w[w] == q[j] * xc[gi][q] for j, w in enumerate(WID)), 'pattern-width supply'
        assert all(n <= xc[gi][q] for n in by_t.values()), 'more than one role per bin/time'
    assert all(call_count[t] == need[t] for t in range(len(order))), 'flow call width demand'
    slots = []
    for gi, (cap, ts) in enumerate(G):
        bins = groups[G[gi]]
        offset = 0
        for q, n in sorted(xc[gi].items()):
            res = color_pattern(n, q, zc[gi, q], WID)
            assert len(res) == n
            for b, it in zip(bins[offset:offset + n], res):
                z = 0
                for t, w in sorted(it):
                    slots.append((t, w, *b, z))
                    z += w
                assert z <= cap
            offset += n
        assert offset == len(bins)
    available = {t: collections.defaultdict(list) for t in range(len(order))}
    for t in available:
        for h, w in enumerate(providers[disp[tuple(order[t])]]['widths']):
            available[t][w].append(h)
    final = []
    for t, w, o, c, p, z in sorted(slots):
        final.append([t, available[t][w].pop(), o, c, p, z])
    assert not any(v for d in available.values() for v in d.values())
    fill = {'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'dispatch_overrides': [], 'method': a.method, 'rows': sorted(final)}
    result, _, _ = owner.check(T, order, fill, disp, None, plan, template, providers)
    profile = {int(k): v for k, v in result['profile'].items()}
    assert collections.Counter(profile) == profile_mix, 'realized profile differs from the pattern-mix profile'
    assert result['live'] == live
    k_lo, k_hi, pr = price(profile, T, rel)
    payload_sha = {}
    prov_out = {pid: {'actual_paid_profile': {str(r): n for r, n in providers[pid]['actual_paid_profile'].items()}, 'widths': providers[pid]['widths']} for pid in providers}
    for n, obj in [('ORDER.json', order), ('FILL.json.gz', fill), ('DISPATCH.json', dispatch), ('PROFILE.json', {str(k): v for k, v in sorted(profile.items())}), ('PROVIDERS.json', prov_out)]:
        save(out / n, obj)
        payload_sha[n] = hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    check = dict(result, status='PASS_VENDORED_PR2839_OWNER_ENGINE_CHECK', solver=status, solve_seconds=solve_seconds, total_seconds=time.time() - t0, chronology=a.chronology, T=T, calls=len(order),
                 physical=result['live'] + HELPERS + CENTRES + a.buffers + GUARDS, physical_formula='live + 408 helpers + 8 centres + %d private buffers + 2 guards' % a.buffers,
                 inventory={pid: dict(sorted(collections.Counter(providers[pid]['widths']).items())) for pid in providers}, local=loc0, engine_sha256=ENGINE_SHA, catalogue=a.catalogue,
                 pattern_mix={('%d:%s' % (cap, pattern_name(WID, counts))): n for (cap, counts), n in sorted(target.items())}, payload_sha256=payload_sha, seed=a.seed, **pr)
    save(out / 'OWNER-CHECK.json', check)
    log('OWNER_CHECK_PASS', out, 'roles', result['roles'], 'idle', result['idle'], 'physical', check['physical'])
    log('KAPPA', pr['kappa_lower_decimal'], '..', pr['kappa_upper_decimal'], 'cap', rel['cap_upper_decimal'], 'gap %.3e' % pr['gap_to_relaxation_cap'], 'gain vs PR2917 claim %.4e' % pr['gain_vs_PR2917_claim_float'], 'gain vs PR2930 claim %.4e' % pr['gain_vs_PR2930_claim_float'], 'gain vs PR2966 %.6e' % pr['gain_vs_PR2966_float'])


if __name__ == '__main__':
    main()
