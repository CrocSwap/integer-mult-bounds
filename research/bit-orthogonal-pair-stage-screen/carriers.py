#!/usr/bin/env python3
# Predecessors: eumemic (PR555, research/e8-bit-p111: gen_p3.py, the frozen L3 plan, punct.json and discovery/search.py);
# DreamingOfClouds (PR589 tuned package: xcheck_p.py); navinor (PR1084 orthogonal-pair decoders).
# Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""Helper count R(P) of PR555's real construction (gen_p3.make/build) for other punctured reader sets P.

    PYTHONPATH=<numpy site> python3 -B research/bit-orthogonal-pair-stage-screen/carriers.py \
        [--out CARRIERS.json.gz] [--workers 4] [--budget SECONDS] [--tiers ship,j5,j4,j3,j2]

Provenance of the shipped receipt CARRIERS.json.gz: built once by
    PYTHONPATH=<numpy site> python3 -B research/bit-orthogonal-pair-stage-screen/carriers.py --workers 4 --budget 1140
with Python 3.14.4 and numpy 2.5.4 (cp314 wheel, sha256
d549420b8858885cea8838a727842249218b9c1da24dd517e25c9c7a948310a3; numpy is needed only by the pinned gen_p3 stack, not by
the stdlib scripts of this package); wall time 1142 s on 4 workers.  The time cap left 648/929 j = 3 and 1473/3977 j = 2
sets not run (recorded as 'not-run (time cap)').  That run wrote indented JSON with an extra 'pricing' section; the
receipt was then re-serialised by write_receipt() (the writer this script now uses) with the 'pricing' section dropped
and every build record unchanged; pricing is done by screen.py ('own_R').  R(P) values are from a BOUNDED receiver
search (below), so they are upper bounds on the minimum of R over gen_p3 receiver choices for P (frozen plan,
thirds seed 552), not proven minimal.

For each reader set P (nine eligible lines from census.py) gen_p3.build is run with P as the punctured set, the frozen
plan research/e8-bit-p111/data/plan-l3.json, plan_thirds seed 552 and punct.json's nodeopt, iterating the extra
carriers exactly as gen_p3.make does (at most 20 'missing' rounds).  R(P) = 420 + 9 + extra_carriers + junk_wires.

Receiver policy (gen_p3 has a default: rcvsel=None keeps the plan's receivers and forces one receiver per p; PR555's
shipped receivers came from discovery/search.py's random draws): minimise R over rcvsel in {1,2,3}^P by block-group
coordinate descent.  Lines p are grouped by the complementary block B = comp(blk(p)) whose mini-node rewrites their
free keepers; each step enumerates all 3^|group| receiver choices of one group with the others fixed (ties keep the
current choice, else the lexicographically smallest); sweeps repeat until one makes no change.  Two starts: the
effective default and (tiers ship/j5 only) the all-3 choice; tiers ship/j5/j4 sweep to convergence (at most 6
sweeps; a converged run is a group-wise local minimum), tiers j3/j2 make ONE sweep from the default (no convergence
check).  This is a bounded search, not a proof of minimality of R(P).

Search builds use NODEOPT = 1, a no-op decoder_rows and stop before PWordL.build (R = helper count; search.py notes
the node effort does not change R).  The selected receivers are then rebuilt by the unmodified gen_p3.build with
punct.json's nodeopt (tiers ship/j5/j4) or NODEOPT = 1 (tiers j3/j2), including gen_p3.decoder_rows and every internal
assert; tiers ship/j5/j4 are also replayed by research/e8-bit-p111-tuned/code/xcheck_p.py (in-process check()).
Scope: the built words keep the dead root duals LIVE; only the reader set P changes.  The dead-dual puncturing (and the
cost-6 COPY realisation) is not modelled by gen_p3.
"""
import argparse
import gzip
import hashlib
import importlib.util
import itertools
import json
import multiprocessing as mp
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CODE = REPO / 'research/e8-bit-p111/code'
PINNED = {
    'research/e8-bit-p111/code/gen_p3.py': '438b83f10d70ceca7cf78049420204b7de2dc61682f913c50a62596106ad84cd',
    'research/e8-bit-p111/code/planio.py': 'c0a687f61aed29455cea953d8a3e49a32136edb3cd4213c46880c146a6ca7fa3',
    'research/e8-bit-p111/code/pwordl.py': '6d8fccd44508e4705b6446e0a64482a5221a3efc5663c5ca7ae90d44581ac50a',
    'research/e8-bit-p111/code/nodeopt.py': '6a5896f60b1fe05c41ab28ce822dff782c635e12d0c74fad20b5ce2a4010fa3f',
    'research/e8-bit-carrier-skeleton/code/skeleton/e8.py':
        '721d859a6517d665ca84d03ef89668da3aae7433ffb0ee47faf37f2aeb85450e',
    'research/e8-bit-carrier-skeleton/code/skeleton/geom.py':
        'bb356568fa05e7bfd5fcd9012903611cf742729a99b4dc3a13685355b2678ae3',
    'research/e8-bit-carrier-skeleton/code/skeleton/gen.py':
        '7cdcf48078ed4beacd2e240aa8145e4aa6984558748d07659cb1b252786e073a',
    'research/e8-bit-carrier-skeleton/code/skeleton/wordkit.py':
        '2b6c12d96f24a4e81f2c807827c2b74cf80037367fc8034e8c871dd5ce008351',
    'research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json':
        'd69ffe3326140bc541b8f1639e02db43a5835ab8ca02cc742b5bee2bf2ef1ba9',
    'research/e8-bit-p111/data/plan-l3.json': 'd5c2494b4baae801143049e172db303b3c8e25a002e9d9715a1d79dcb2d74c58',
    'research/e8-bit-p111/data/punct.json': 'dd371e1d6fe57602f242920b582ec4c133efc8ede4a849fd701ac90b7f6e1853',
    'research/e8-bit-p111-tuned/code/xcheck_p.py': 'af3decc877e27c00001cf56f50c6c09566e8e101297ab34c7860aed96a06d80e',
    'research/bit-orthogonal-pair-stage-screen/CENSUS.json':
        'b84bbba90a732bf4952a45fb420a4deec4a4160e21e3565d607f5d191e41a18e',
    'research/bit-orthogonal-pair-stage-screen/census.py':
        'ae3e4084698206f661cdb00230dfb0eac2639aae5c66e26cda0a7a1e2a8370e0',
}
SHIPPED_P = [10, 15, 51, 53, 56, 66, 72, 89, 111]
R_L3, N_TOTALS = 420, 9


def sha(rel):
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()


def check_pins():
    bad = {rel: sha(rel) for rel in PINNED if sha(rel) != PINNED[rel]}
    assert not bad, ('input pins', bad)


# ------------------------------------------------------------------------------------------------ worker state
S = {}


class _Done(Exception):
    def __init__(self, R):
        super().__init__(R)
        self.R = R


def _init(deadline):
    check_pins()
    sys.path.insert(0, str(CODE))
    import gen_p3                                       # noqa: E402  (pinned path, checked below)
    assert Path(gen_p3.__file__).resolve() == (CODE / 'gen_p3.py').resolve()
    from geom import Geom
    from planio import load_plan
    prm = json.load(open(REPO / 'research/e8-bit-p111/data/punct.json'))
    gen_p3.NODEOPT[0] = 1                               # search effort; the final builds of tiers ship/j5/j4 use prm
    G = Geom()
    sol = load_plan(str(REPO / 'research/e8-bit-p111/data/plan-l3.json'))
    pt = gen_p3.plan_thirds(G, sol, random.Random(prm['thirds_seed']))
    assert pt[0] != 'failed'
    dcellof, keepline, home, qhostD6, zz = gen_p3.derive(G, sol, pt[0])
    spec = importlib.util.spec_from_file_location('xcheck_p', REPO / 'research/e8-bit-p111-tuned/code/xcheck_p.py')
    xc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xc)

    class FastPWordL(gen_p3.PWordL):
        def build(self, rows):
            raise _Done(self.nh)
    S.update(gen_p3=gen_p3, G=G, sol=sol, fl=pt[0], asg=pt[1], zz=zz, prm=prm, xc=xc, deadline=deadline,
             real=(gen_p3.PWordL, gen_p3.decoder_rows), fast=(FastPWordL, lambda cvals, live: {}))


def _mode(fast):
    g = S['gen_p3']
    g.PWordL, g.decoder_rows = S['fast'] if fast else S['real']


def zzp(p):
    G = S['G']
    return sorted(H for H in S['zz'] if G.phi[H[0]] == G.phi[p])


def default_sel(P):
    """the rcvsel equivalent of gen_p3's default (rcvsel None): plan receivers, first (z,z) D6 forced if none is p"""
    rcv = S['sol']['rcv']
    out = {}
    for p in P:
        b = sum(1 << i for i, H in enumerate(zzp(p)) if rcv[H] == p)
        out[p] = b or 1
    return out


def run_build(P, sel, fast):
    """gen_p3.make's extra-carrier iteration with a given rcvsel; returns a status dict"""
    g = S['gen_p3']
    _mode(fast)
    extras = {}
    try:
        for it in range(21):
            try:
                res = g.build(S['G'], S['sol'], P, S['fl'], S['asg'], extras=extras, verbose=False, rcvsel=sel)
            except _Done as d:
                x = d.R - R_L3 - N_TOTALS
                ne = sum(len(v) for v in extras.values())
                return dict(ok=True, R=d.R, extra_carriers=ne, junk_wires=x - ne, extras=extras, rounds=it + 1)
            if res[0] == 'missing':
                if it == 20:
                    return dict(ok=False, reason='still missing after 20 extra-carrier rounds', extras=extras)
                for B, ls in res[1].items():
                    extras[B] = sorted(set(extras.get(B, [])) | set(ls))
                continue
            W, word = res
            return dict(ok=True, R=word['R'], extra_carriers=word['stats']['extra_carriers'],
                        junk_wires=word['stats']['junk_wires'], rcv_flips=word['stats']['rcv_flips'], extras=extras,
                        rounds=it + 1, word=word)
    except AssertionError as e:
        return dict(ok=False, reason='AssertionError: ' + str(e)[:160], extras=extras)
    finally:
        _mode(False)


def search(P, starts_names, max_sweeps):
    G = S['G']
    groups = {}
    for p in P:
        groups.setdefault(G.comp[G.blk[p]], []).append(p)
    groups = [sorted(groups[B]) for B in sorted(groups)]
    cache = {}

    def ev(sel):
        key = tuple(sel[p] for p in P)
        if key not in cache:
            r = run_build(P, dict(sel), True)
            cache[key] = r['R'] if r['ok'] else 10 ** 9
        return cache[key]

    starts = [(n, default_sel(P) if n == 'default' else {p: 3 for p in P}) for n in starts_names]
    runs = []
    for name, sel in starts:
        cur = dict(sel)
        best = ev(cur)
        sweeps = 0
        while True:
            sweeps += 1
            changed = False
            for grp in groups:
                curv = tuple(cur[p] for p in grp)
                opts = []
                for ch in itertools.product((1, 2, 3), repeat=len(grp)):
                    trial = dict(cur)
                    trial.update(zip(grp, ch))
                    opts.append((ev(trial), ch != curv, ch))
                r, _, ch = min(opts)
                if r < best:
                    cur.update(zip(grp, ch))
                    best = r
                    changed = True
            if not changed or sweeps >= max_sweeps:
                break
        runs.append(dict(start=name, R=best, sweeps=sweeps, converged=not changed, sel=dict(cur)))
    top = min(runs, key=lambda z: (z['R'], [z['sel'][p] for p in P]))
    return top, runs, len(cache), [len(g) for g in groups]


def task_screen(item):
    """tiers j3/j2, phase 1: R of the default and the all-3 receivers (fast search builds)"""
    tier, P, meta = item
    a = run_build(P, default_sel(P), True)
    b = run_build(P, {p: 3 for p in P}, True)
    return dict(tier=tier, P=P, **meta, screen=dict(default_R=a.get('R'), all3_R=b.get('R'),
                                                   default_fail=a.get('reason'), all3_fail=b.get('reason')))


def task(item):
    tier, P, meta = item
    t0 = time.time()
    if time.time() > S['deadline']:
        return dict(tier=tier, P=P, status='not-run (time cap)', **meta)
    out = dict(tier=tier, P=P, **meta)
    if 'screen' in meta:
        out.pop('screen')
    d0 = run_build(P, None, True)                   # gen_p3 default receivers (rcvsel None)
    out['default_receivers'] = dict(ok=d0['ok'], R=d0.get('R'), reason=d0.get('reason'))
    starts, sweeps = (('default', 'all3'), 6) if tier in ('ship', 'j5') else (('default',), 6) \
        if tier == 'j4' else (('default',), 1)
    top, runs, nev, gsz = search(P, starts, sweeps)
    out['search'] = dict(groups=gsz, evaluations=nev, max_sweeps=sweeps,
                         starts={r['start']: dict(R=r['R'], sweeps=r['sweeps'], converged=r['converged'])
                                 for r in runs},
                         starts_agree=len({r['R'] for r in runs}) == 1)
    sel = top['sel']
    if top['R'] >= 10 ** 9:
        out.update(status='build-failed', reason='every searched receiver choice failed')
        return out
    full = tier in ('ship', 'j5', 'j4')
    S['gen_p3'].NODEOPT[0] = S['prm']['nodeopt'] if full else 1
    fb = run_build(P, sel, False)
    S['gen_p3'].NODEOPT[0] = 1
    out['receivers'] = {str(p): sel[p] for p in P}
    if not fb['ok']:
        out.update(status='build-failed', reason=fb['reason'])
        return out
    assert fb['R'] == top['R'], ('final build R differs from search R', fb['R'], top['R'])
    w = fb['word']
    out.update(status='built', R=fb['R'], x=fb['R'] - R_L3 - N_TOTALS, extra_carriers=fb['extra_carriers'],
               junk_wires=fb['junk_wires'], rcv_flips=fb['rcv_flips'],
               extra_carrier_lines={str(B): v for B, v in sorted(fb['extras'].items())},
               build_asserts_and_decoder_rows='PASS', nodeopt=S['prm']['nodeopt'] if full else 1,
               word_v=w['v'], word_sha256=hashlib.sha256(json.dumps(w, sort_keys=True).encode()).hexdigest())
    if full:
        try:
            wj = json.loads(json.dumps(w))
            W, lab, fl, H, C, info = S['xc'].check(wj)
            ok = all(H.values()) and all(C.values()) and lab['punctured'] == 9 and \
                sum(x['rank'] for x in fl['totals']) == 63
            out['xcheck_p'] = 'PASS' if ok else 'FAIL interface: ' + json.dumps(
                dict(H=H, C=C, punctured=lab['punctured']))
        except Exception as e:                       # noqa: BLE001  (xcheck_p raises Reject on the first failure)
            out['xcheck_p'] = 'FAIL ' + type(e).__name__ + ': ' + str(e)[:160]
    print('done', tier, P, out.get('R'), out.get('xcheck_p'), round(time.time() - t0, 1), file=sys.stderr, flush=True)
    return out


# ------------------------------------------------------------------------------------------------ domain
def domain():
    cen = json.load(open(HERE / 'CENSUS.json'))
    hi = {tuple(r['P']): r for r in cen['admissible_P_with_j_at_least_4']}
    spec = importlib.util.spec_from_file_location('census_mod', HERE / 'census.py')
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)
    Gm = cm.gram_from_lines()
    ROW = cm.b0_rows(Gm)
    ROWIDX = {r: a for a, r in enumerate(ROW)}
    elig = cen['eligibility']['eligible_outside_0_7']
    by_j = {}
    for P in itertools.combinations(sorted(elig), 9):
        rec = cm.analyse(list(P), Gm, ROW, ROWIDX)
        if rec is None:
            continue
        by_j.setdefault(rec['j'], []).append((list(P), rec['dead']))
    dist = {str(j): len(v) for j, v in sorted(by_j.items())}
    assert dist == cen['j_distribution']['admissible_EZA'], ('census j distribution', dist)
    for j in (4, 5):
        assert sorted(tuple(P) for P, _ in by_j[j]) == sorted(k for k, r in hi.items() if r['j'] == j)
        for P, dead in by_j[j]:
            assert hi[tuple(P)]['dead_duals'] == dead
    return by_j, dist


def write_receipt(obj, path):
    """deterministic gzip receipt: compact sorted JSON + newline, gzip level 9, empty file name, mtime 0"""
    data = (json.dumps(obj, sort_keys=True, separators=(',', ':')) + '\n').encode()
    with open(path, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', compresslevel=9, fileobj=raw, mtime=0) as gz:
        gz.write(data)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(HERE / 'CARRIERS.json.gz'))
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--budget', type=float, default=1800.0, help='seconds; sets not started by then are not run')
    ap.add_argument('--tiers', default='ship,j5,j4,j3,j2')
    ap.add_argument('--limit', type=int, default=0, help='debug: first N sets of each of tiers j3/j2 only')
    args = ap.parse_args(argv)
    t0 = time.time()
    check_pins()
    by_j, dist = domain()
    tiers = args.tiers.split(',')
    items = []
    if 'ship' in tiers:
        items.append(('ship', SHIPPED_P, dict(j=1, dead_duals=[87])))
    for name, j in (('j5', 5), ('j4', 4), ('j3', 3), ('j2', 2)):
        if name in tiers:
            sets = sorted(by_j[j])
            if args.limit and j <= 3:
                sets = sets[:args.limit]
            items += [(name, P, dict(j=j, dead_duals=dead)) for P, dead in sets]
    hi = [it for it in items if it[0] in ('ship', 'j5', 'j4')]
    lo = [it for it in items if it[0] in ('j3', 'j2')]
    deadline = t0 + args.budget
    with mp.Pool(args.workers, initializer=_init, initargs=(deadline,)) as pool:
        res = list(pool.imap(task, hi, chunksize=1))
        scr = list(pool.imap(task_screen, lo, chunksize=8))
        # phase 2: one-sweep search in ascending order of (phase-1 R - nine-stage wall 4(111 - j)), phase-1 R = best of
        # the default / all-3 receivers, until the time cap
        big = 10 ** 9
        scr.sort(key=lambda r: (min(r['screen']['default_R'] or big, r['screen']['all3_R'] or big) - 4 * (111 - r['j']),
                                ['j3', 'j2'].index(r['tier']), r['P']))
        swept = list(pool.imap(task, [(r['tier'], r['P'], dict(j=r['j'], dead_duals=r['dead_duals'],
                                                                 screen=r['screen'])) for r in scr], chunksize=1))
    for r, w in zip(scr, swept):
        w['screen'] = r['screen']
    res += swept
    # control: shipped P with the frozen punct.json receivers (a plain gen_p3.make-style build) is R = 439, x = 10
    _init(deadline + 10 ** 6)
    sel = {int(k): v for k, v in S['prm']['receivers'].items()}
    S['gen_p3'].NODEOPT[0] = 1
    c = run_build(SHIPPED_P, sel, False)
    control = dict(P=SHIPPED_P, receivers=S['prm']['receivers'], R=c['R'], extra_carriers=c['extra_carriers'],
                   junk_wires=c['junk_wires'], rcv_flips=c['rcv_flips'], expected='R 439, extra_carriers 10, '
                   'junk_wires 0, rcv_flips 10 (PR555 shipped word)')
    assert (c['R'], c['extra_carriers'], c['junk_wires'], c['rcv_flips']) == (439, 10, 0, 10), control
    res.sort(key=lambda r: (['ship', 'j5', 'j4', 'j3', 'j2'].index(r['tier']), r['P']))
    cov, summ = {}, {}
    for t in ['ship', 'j5', 'j4', 'j3', 'j2']:
        rs = [r for r in res if r['tier'] == t]
        if not rs:
            continue
        built = [r for r in rs if r['status'] == 'built']
        cov[t] = dict(domain=len(rs), built=len(built), failed=sum(r['status'] == 'build-failed' for r in rs),
                      not_run=sum(r['status'].startswith('not-run') for r in rs))
        if t in ('j3', 'j2'):
            sm = sorted(min(r['screen']['default_R'] or 10 ** 9, r['screen']['all3_R'] or 10 ** 9) for r in rs)
            wall = 4 * (111 - int(t[1]))
            cov[t].update(screened=len(rs), screen_failed=sum(x >= 10 ** 9 for x in sm),
                          screen_R_min=sm[0], screen_R_hist={str(x): sm.count(x) for x in sorted(set(sm))},
                          nine_stage_wall_R_max=wall, swept_with_R_at_most_wall=sum(r['R'] <= wall for r in built),
                          swept_order='ascending phase-1 R - 4(111 - j) (phase-1 R: best of default / all-3 receivers)')
        if built:
            xs = sorted(r['x'] for r in built)
            summ[t] = dict(R_min=xs[0] + 429, R_max=xs[-1] + 429,
                           x_hist={str(x): xs.count(x) for x in sorted(set(xs))},
                           xcheck_pass=sum(r.get('xcheck_p') == 'PASS' for r in built),
                           xcheck_run=sum('xcheck_p' in r for r in built),
                           default_receivers_R_hist={str(k): v for k, v in sorted(
                               __import__('collections').Counter(r['default_receivers']['R'] for r in built).items(),
                               key=lambda kv: (kv[0] is None, kv[0] or 0))},
                           starts_disagree=sum(not r['search']['starts_agree'] for r in built))
    out = dict(
        package='research/bit-orthogonal-pair-stage-screen', script='carriers.py',
        claim_scope='helper counts R(P) = 420 + 9 + extra carriers + junk wires of PR555 gen_p3.build for other reader '
                    'sets P (frozen plan, thirds seed 552); receivers by bounded search (not proven minimal); the built '
                    'words keep the dead duals LIVE (dead-dual puncturing and cost-6 COPYs are not modelled by gen_p3)',
        receiver_policy=__doc__.split('Receiver policy')[1].split('Search builds')[0].strip(),
        build_policy=__doc__.split('Search builds')[1].split('Scope:')[0].strip(),
        inputs={rel: PINNED[rel] for rel in sorted(PINNED)},
        census_j_distribution_recomputed=dist, control_shipped_frozen_receivers=control,
        coverage=cov, summary=summ, results=res)
    write_receipt(out, args.out)
    print('CARRIERS coverage', json.dumps(cov, sort_keys=True))
    print('CARRIERS summary', json.dumps(summ, sort_keys=True))
    print('wall seconds', round(time.time() - t0, 1))


if __name__ == '__main__':
    main()
