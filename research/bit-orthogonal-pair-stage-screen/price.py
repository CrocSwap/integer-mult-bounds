#!/usr/bin/env python3
# Predecessors: navinor (PR1084, research/bit-orthogonal-pair-decoders: orthogonal-pair label decoders, cost-6 terms,
# the shipped P111 dual root and the P110 / P102 decoder constants); eumemic (PR555, research/e8-bit-p111: the punctured
# R439 word, its nine- and eleven-stage prices and frozen hosting selections); DreamingOfClouds (PR589 tuned word and
# tune/fastc.py; PR545 punctured-star unit, rank-mass identity and adapt.py; PR510/PR463 nine-stage template); PR493
# eleven-stage chain (research/e8-bit-carrier-skeleton) and DaysSky's PR442 idle-axis hosting (hosting_core.windows);
# research/bit589-width-packing (slot model of the PR589 hosting).
# Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""Exact stdlib pricer for hypothetical punctured bit units P(111-j) of the PR589 word at nine and eleven stages.

    python3 -I -B research/bit-orthogonal-pair-stage-screen/price.py [--json OUT.json]

API:  price(dead_lines, cost6, L, *, index='geom', variant='transplant', R=439, readers=None) -> dict
      (readers = nine geometry lines: 'transplant-swap' proxy for a different punctured reader set)
      price_uniform(j, cost6, L, *, R=439) -> dict   (the 'uniform' variant)

Model (a pricing screen, not a construction):
  * Templates.  L = 9: PR510's chain (PR463 template, K = 4 pairs, T = 32 replicas, m = 64, W = 2KTv = 256v).
    L = 11: PR493's chain as parameterised by PR545's adapt.py (K = 5, T = 8, m = 78, W = 80v).  The parameters are
    read from the pinned source files; the idle children (slot capacities and hosting windows) are rebuilt from the
    pinned recipe() of each emitter plus the idle-insertion rule of both emitters (anchored by exact text matches) and
    PR442's hosting_core.windows.  Per replica every slot index holds 2v families.
  * Hosting (slot model).  Every call has R width-8 helper residuals; a slot of capacity c holds at most floor(c/8)
    of them and keeps an idle child c - 8u.  Whole hosting (no banks) requires a stage->slot flow saturating all L*R
    residuals per replica (max-flow over the pinned windows); the aggregate form is the wall R <= 4v (L = 9) and
    11 R <= 64 v (L = 11).  Among whole-hosted placements the moment-minimising one is computed exactly: the
    per-copy cost k -> G(rmin + 8k) is concave, so a minimiser has at most one partially idle copy; candidates are
    enumerated with a certified per-unit lower bound and compared with the pinned engine's interval logarithm and
    exponential at c_hat = c + 10^-24 (bad-residue surcharge included).  The certificate: every whole-hosted
    placement has moment >= that of the chosen one at c_hat, which the engine shows is > 1.
  * Local profile ('transplant').  PR589 word's paid climbs (exact replay as in tune/wlib.py) and COPY ranks, with
    the climbs of source register x_b and target register y_b removed for every dead live line b, and cost6 COPY
    children of rank 7 changed to rank 6; helpers (R = 439) unchanged.  The local mass must equal 8R + 14v' + cst'.
    'uniform': the same with j copies of the AVERAGE (x_t, y_t) climb pattern over all 111 live lines removed
    (fractional counts, priced with the engine's rational moment()).
  * Price.  c = certified lower endpoint (10^-24 grid) of the moment of calls*local + T*idle at (m, W).
    Rows violating whole hosting are hostable = false; their reported c is the price IF the overflow residuals were
    hosted in exact width-64 banks (PR510/PR443 bank rule, live stock grows; minimal banks, not optimised).

Scope: no word is built; the transplant profile, the cost-6 COPY realisation (PR620) and owner maps are hypotheses.
"""
import argparse
import ast
import gzip
import hashlib
import importlib.util
import itertools
import json
import re
import sys
from collections import Counter
from decimal import Decimal, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRID = Q(1, 10 ** 24)
R0 = 439

PINS = {
    'engine': ('research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines/moment.py',
               '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482'),
    'hosting_core': ('research/e8-bit-carrier-skeleton/code/hub/idle-axis-hosting/hosting_core.py',
                     'd8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3'),
    'emit11': ('research/e8-bit-carrier-skeleton/code/eleven/emit.py',
               'b0b25955875625ed63f82690f83aef976e3e9a978ae6620b23a23fc1207acd46'),
    'adapt545': ('research/e8-bit-p111/vendor/pr545/code/adapt.py',
                 'b9a50303147a3003ad94fc4b1a822d4fca7f9b9e917d165e3c45152575302a0e'),
    'global9': ('research/e8-bit-p111/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py',
                '6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8'),
    'config9': ('research/e8-bit-p111/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/config.py',
                '283d7fad45155ee91e704d63ec947cf4a60aeff5cc43510bc0e835f7da7d8767'),
    'wlib': ('research/e8-bit-p111-tuned/tune/wlib.py',
             'a37fdf3cdf5f62945c2a90193401c0e9edc9dd3cda8d8cb36a3b9c329ebe4dbc'),
    'word589': ('research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
                'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'),
    'expected589': ('research/e8-bit-p111-tuned/tune/EXPECTED.json',
                    'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4'),
    'expected555': ('research/e8-bit-p111/EXPECTED.json',
                    '7c2675fd49afd7e328606399a4421fd49c43fe8a6c5b57154cc908c00588abe2'),
    'selection9': ('research/e8-bit-p111-tuned/data/selection9-p111.json',
                   '4ab1ed4529683cd184987f8bc3031fb7408b9cd22c25ab9cf541a8aaf896eaf1'),
    'hosting11': ('research/e8-bit-p111/data/hosting11-p111.json',
                  '1f5a1142e0119483cabf9a4d99094d988014d1adaa29370e93f4b4a63d9bfd7f'),
    'pr1084': ('research/bit-orthogonal-pair-decoders/RESULTS.json',
               '7f3d6df3ab4dd9fd4a94ab36c444d777f1b45bf8a25ee880d6c1d8a363362e33'),
}
C_PR589_9 = Q(1733427039589844234749, 10 ** 24)      # selected bit c (PR589, nine stages)
C_PR589_11 = Q(855475950388791987811, 5 * 10 ** 23)  # PR589 README / tune/EXPECTED.json, eleven stages
C_PR555_9 = Q(1733052823330162099157, 10 ** 24)
C_PR555_11 = Q(427652201524503168379, 25 * 10 ** 22)
REM9_PINNED = {2: 13920, 4: 14208, 6: 14208, 7: 21312, 42: 288}   # tune/fastc.py


def require(ok, msg):
    if not ok:
        raise AssertionError(msg)


def _path(key):
    rel, digest = PINS[key]
    p = ROOT / rel
    if digest is not None:
        require(hashlib.sha256(p.read_bytes()).hexdigest() == digest, f'pin mismatch: {rel}')
    return p


def _module(key):
    p = _path(key)
    spec = importlib.util.spec_from_file_location('pinned_' + key, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _json(key):
    return json.loads(_path(key).read_bytes())


ENGINE = _module('engine')
HC = _module('hosting_core')     # module level imports math/collections only; solve() (numpy) is never called
WLIB = _module('wlib')


def dec(x, digits=24):
    with localcontext() as ctx:
        ctx.prec = 60
        return str((Decimal(x.numerator) / Decimal(x.denominator)).quantize(Decimal(1).scaleb(-digits)))


def qstr(x):
    x = Q(x)
    return str(x.numerator) if x.denominator == 1 else f'{x.numerator}/{x.denominator}'


# --------------------------------------------------------------------------------------------- engine wrappers
def certify(P, m, W, rational_path=False):
    """Certified lower endpoint on the 10^-24 grid, bad-residue surcharge included.  Integer profiles go through the
    pinned engine's certify(); fractional ones use the same Decimal bisection to propose and the pinned engine's
    rational moment() to certify moment(c) < 1 < moment(c + 10^-24)."""
    P = {int(r): Q(n) for r, n in P.items() if n}
    require(all(n > 0 and 0 < r < m for r, n in P.items()), 'profile must have positive counts and 0 < r < m')
    if not rational_path and all(n.denominator == 1 for n in P.values()):
        return Q(ENGINE.certify({r: int(n) for r, n in P.items()}, m, W, True)['lower'])
    with localcontext() as ctx:
        ctx.prec = 70
        dq = lambda x: Decimal(x.numerator) / Decimal(x.denominator)
        terms = [(dq(r * n) / Decimal(m * W), (Decimal(m) / Decimal(r)).ln()) for r, n in P.items()]
        fallback = dq(32 * m * sum(P.values())) / Decimal(10 ** 16 * W)
        lm = Decimal(m).ln()
        lo, hi = Decimal(0), Decimal('.003')
        for _ in range(210):
            a = (lo + hi) / 2
            if sum(p * (a * l).exp() for p, l in terms) + fallback * (a * lm).exp() < 1:
                lo = a
            else:
                hi = a
        q = int(((lo + hi) / 2 * 10 ** 24).to_integral_value(rounding=ROUND_FLOOR))
    c = Q(q, 10 ** 24)
    require(ENGINE.moment(P, m, W, c, True)[1] < 1 < ENGINE.moment(P, m, W, c + GRID, True)[0],
            'fractional profile: engine moment does not bracket 1 at the proposed grid point')
    return c


def _G(r, m, c):
    """interval of one child's moment contribution times m*W: r (m/r)^c + 32 m^2 m^c / 10^16 (r > 0), 0 for r = 0"""
    if r == 0:
        return Q(0), Q(0)
    l, u = ENGINE.logarithm(Q(m, r))
    e, f = ENGINE.exponential(c * l, c * u)
    bl, bu = ENGINE.logarithm(Q(m))
    be, bf = ENGINE.exponential(c * bl, c * bu)
    k = Q(32 * m * m, 10 ** 16)
    return r * e + k * be, r * f + k * bf


# --------------------------------------------------------------------------------------------- templates
def _pinned_function(key, name):
    p = _path(key)
    tree = ast.parse(p.read_text())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(fn) == 1, f'{name} not unique in {p}')
    ns = {}
    exec(compile(ast.Module(body=fn, type_ignores=[]), str(p), 'exec'), ns)
    return ns


# the idle-insertion rule of both emitters (exact source anchors checked below)
IDLE_ANCHORS = {
    'global9': ["schedule.append(dict(kind='idle',pair=j,rank=7*(s+1),source_level=-1,target_level=s))",
                "schedule.append(dict(kind='idle',pair=j,rank=7,source_level=s-1,target_level=s))",
                "schedule.append(dict(kind='idle',pair=j,rank=7*(2*K-oldlevel),source_level=oldlevel,target_level=2*K))",
                "if s%2==1 and s<=2*K-3:", "elif s%2==0 and 2<=s<=2*K-2:", "elif s==2*K:"],
    'emit11': ["schedule.append(dict(kind='idle',pair=j,rank=7*(s+1),source_level=-1,target_level=s))",
               "schedule.append(dict(kind='idle',pair=j,rank=7,source_level=s-1,target_level=s))",
               "schedule.append(dict(kind='idle',pair=j,rank=7*(2*K-oldlevel),source_level=oldlevel,target_level=2*K))",
               "if s in range(1,2*K-1,2):", "elif s in range(2,2*K,2):", "elif s==2*K:"],
}


def _template_constants(L):
    if L == 11:
        src = _path('emit11').read_text()
        mt = re.search(r'^H,L,K,T,M=(\d+),(\d+),(\d+),(\d+),(\d+)$', src, re.M)
        H, LL, K, T, M = map(int, mt.groups())
        adapt = _path('adapt545').read_text()
        require('"K,L,M,T=5,11,78,8\\n' in adapt and 'DATA=2*K*V*T' in adapt,
                'PR545 adapt.py keeps K, L, M, T and DATA = 2KVT for the eleven-stage audit')
        ns = _pinned_function('emit11', 'recipe')
        ns['K'] = K
        events = ns['recipe']()
        halving = 3
        key = 'emit11'
    elif L == 9:
        src = _path('global9').read_text()
        require('H,L,K,T,M=8,9,4,REPLICAS,64' in src, 'global_k.py nine-stage defaults')
        mt = re.search(r'^REPLICAS\s*=\s*(\d+)$', _path('config9').read_text(), re.M)
        H, LL, K, T, M = 8, 9, 4, int(mt.group(1)), 64
        events = _pinned_function('global9', 'recipe')['recipe'](K)
        halving = 2
        key = 'global9'
    else:
        raise ValueError('L must be 9 or 11')
    require(LL == L and H == 8 and K == (L - 1) // 2 and M == 1 + 7 * L, 'template constants')
    text = _path(key).read_text()
    require(all(text.count(a) == 1 for a in IDLE_ANCHORS[key]), f'idle-insertion anchors in {key}')
    return dict(L=L, K=K, T=T, m=M, events=events, halving_depth=halving, source=PINS[key][0])


def _schedule(tpl):
    """idle children inserted exactly as the emitters do (rule anchored above); HC.windows-ready event list"""
    K = tpl['K']
    levels = [-1] * K
    out = []
    idx = 0
    for e in tpl['events']:
        if e['kind'] == 'local':
            s, p = e['stage'], e['pair']
            require(levels[p] == s - 1, 'recipe order')
            levels[p] = s
            out.append(dict(kind='local', stage=s, pair=p))
            new = []
            if s % 2 == 1 and s <= 2 * K - 3:
                j = (s + 1) // 2
                require(levels[j] == -1, 'level')
                levels[j] = s
                new.append((j, 7 * (s + 1)))
            elif s % 2 == 0 and 2 <= s <= 2 * K - 2:
                j = s // 2
                require(levels[j] == s - 1, 'level')
                levels[j] = s
                new.append((j, 7))
            elif s == 2 * K:
                for j in range(K):
                    require(levels[j] == 2 * j + 2, 'level')
                    new.append((j, 7 * (2 * K - levels[j])))
                    levels[j] = 2 * K
            for j, rank in new:
                out.append(dict(kind='idle', pair=j, rank=rank, idx=idx))
                idx += 1
        elif e['kind'] == 'bridge':
            out.append(dict(kind='bridge', dst=e['dst'], src=e['src']))
    require(levels == [2 * K] * K, 'all pairs end at level 2K')
    return out


_TPL = {}


def template(L):
    if L in _TPL:
        return _TPL[L]
    tpl = _template_constants(L)
    win = {i: (p, r, frozenset(st)) for i, (p, r, st) in HC.windows(_schedule(tpl)).items() if r > 0}
    require(all(st for _, _, st in win.values()), 'every idle child with rank > 0 has a non-empty window')
    tpl['windows'] = win
    tpl['capacities'] = [win[i][1] for i in sorted(win)]
    # aggregate Hall wall: R <= min over stage subsets of 2v * units(N(S)) / |S|
    best = None
    for k in range(1, L + 1):
        for S in itertools.combinations(range(L), k):
            units = sum(r // 8 for _, r, st in win.values() if st & set(S))
            ratio = Q(2 * units, k)
            best = ratio if best is None or ratio < best else best
    tpl['wall_ratio'] = best              # whole hosting needs R <= wall_ratio * v (necessary; flow checked per row)
    _TPL[L] = tpl
    return tpl


def live_stock(tpl, v):
    return 2 * tpl['K'] * tpl['T'] * v


def deficit(tpl, v, cst):
    return tpl['T'] * (2 * tpl['K'] * v - tpl['L'] * cst)


# --------------------------------------------------------------------------------------------- hosting slot model
def _maxflow(cap_stage, slot_units, windows):
    """stage -> slot max-flow (all integer); returns value and per-stage hosted counts"""
    stages = sorted(cap_stage)
    slots = sorted(slot_units)
    n = 2 + len(stages) + len(slots)
    src, snk = 0, n - 1
    sid = {s: 1 + i for i, s in enumerate(stages)}
    tid = {t: 1 + len(stages) + i for i, t in enumerate(slots)}
    cap = [[0] * n for _ in range(n)]
    for s in stages:
        cap[src][sid[s]] = cap_stage[s]
    for t in slots:
        cap[tid[t]][snk] = slot_units[t]
        for s in windows[t]:
            if s in sid:
                cap[sid[s]][tid[t]] = 10 ** 9
    flow = 0
    while True:
        prev = [-1] * n
        prev[src] = src
        queue = [src]
        for x in queue:
            for y in range(n):
                if prev[y] < 0 and cap[x][y] > 0:
                    prev[y] = x
                    queue.append(y)
        if prev[snk] < 0:
            break
        b, y = 10 ** 18, snk
        while y != src:
            b = min(b, cap[prev[y]][y])
            y = prev[y]
        y = snk
        while y != src:
            cap[prev[y]][y] -= b
            cap[y][prev[y]] += b
            y = prev[y]
        flow += b
    hosted = {s: cap_stage[s] - cap[src][sid[s]] for s in stages}
    return flow, hosted


def _classes(tpl, v):
    cl = {}
    for i, (p, r, st) in sorted(tpl['windows'].items()):
        c = cl.setdefault(r, dict(idx=[], umax=r // 8, rmin=r % 8, copies=0))
        c['idx'].append(i)
        c['copies'] += 2 * v
    return cl


def _distribute(tpl, v, cl, idle):
    """idle: {cap: [k, k, ...]} unused units of the idle copies of each class -> used units per slot index.
    Tries the balanced split first, then every split of each class (only if needed)."""
    def used(split):
        U = {}
        for cap, c in cl.items():
            for i in c['idx']:
                U[i] = 2 * v * c['umax']
            for i, ks in zip(c['idx'], split[cap]):
                U[i] -= sum(ks)
        return U

    def balanced(cap):
        ks = sorted(idle.get(cap, []), reverse=True)
        parts = [[] for _ in cl[cap]['idx']]
        for n, k in enumerate(ks):
            parts[n % len(parts)].append(k)
        return parts

    splits = {cap: balanced(cap) for cap in cl}
    yield used(splits)
    for cap in cl:
        ks = sorted(idle.get(cap, []), reverse=True)
        if len(cl[cap]['idx']) == 2 and ks:
            for a in range(len(ks) + 1):
                alt = dict(splits)
                alt[cap] = [ks[:a], ks[a:]]
                if all(len(x) <= 2 * v for x in alt[cap]):
                    yield used(alt)


def _vertex_candidates(cl, S, ostar, N):
    """all sub-placements of exactly N units outside the n* fully idle best-class copies:
    fully idle copies of the other classes plus at most one partially idle copy (any class)."""
    capstar, kstar = ostar
    nstar = (S - N) // kstar
    others = [cap for cap in sorted(cl) if cl[cap]['umax'] >= 1 and cap != capstar]
    partials = [(None, 0)] + [(cap, k) for cap in sorted(cl) for k in range(1, cl[cap]['umax'])]
    out = []
    for pc, pk in partials:
        rest = N - pk
        if rest < 0:
            continue
        if pc == capstar and nstar + 1 > cl[capstar]['copies']:
            continue

        def rec(i, left, chosen):
            if i == len(others):
                if left == 0:
                    out.append((dict(chosen), (pc, pk) if pc is not None else None))
                return
            cap = others[i]
            u = cl[cap]['umax']
            avail = cl[cap]['copies'] - (1 if pc == cap else 0)
            for n in range(0, min(avail, left // u) + 1):
                if n:
                    chosen[cap] = n
                rec(i + 1, left - n * u, chosen)
                chosen.pop(cap, None)
        rec(0, rest, {})
    return out


def idle_optimum(L, v, R, c_eval):
    """Certified moment-minimising whole-hosted placement of the slot model at c_eval.
    Returns (idle children per replica, info) or (None, info) when whole hosting is impossible."""
    tpl = template(L)
    m = tpl['m']
    cl = _classes(tpl, v)
    units = sum(c['copies'] * c['umax'] for c in cl.values())
    S = units - L * R
    info = dict(slack_units_per_replica=S, capacity_units_per_replica=units)
    if S < 0:
        return None, info
    G = {}

    def g(r):
        if r not in G:
            G[r] = _G(r, m, c_eval)
        return G[r]

    D = {}
    for cap, c in cl.items():
        for k in range(1, c['umax'] + 1):
            a, b = g(c['rmin'] + 8 * k), g(c['rmin'])
            D[cap, k] = (a[0] - b[1], a[1] - b[0])
    phi = {o: (d[0] / o[1], d[1] / o[1]) for o, d in D.items()}
    full = [(cap, c['umax']) for cap, c in cl.items() if c['umax'] >= 1]
    ostar = min(full, key=lambda o: phi[o][1])
    require(all(phi[ostar][1] < phi[o][0] for o in phi if o != ostar), 'best per-unit option not certified unique')
    phi2 = min(phi[o][0] for o in phi if o != ostar)
    capstar, kstar = ostar
    Nmin = max(0, S - kstar * cl[capstar]['copies'])
    Nmin += (S - Nmin) % kstar
    cands = []
    best_hi = None
    N = Nmin
    while N <= S:
        lb = (S - N) * phi[ostar][0] + N * phi2
        if best_hi is not None and lb > best_hi:
            break
        nstar = (S - N) // kstar
        for chosen, part in _vertex_candidates(cl, S, ostar, N):
            lo = nstar * D[ostar][0]
            hi = nstar * D[ostar][1]
            for cap, n in chosen.items():
                lo += n * D[cap, cl[cap]['umax']][0]
                hi += n * D[cap, cl[cap]['umax']][1]
            if part:
                lo += D[part][0]
                hi += D[part][1]
            cands.append((hi, lo, nstar, chosen, part))
            best_hi = hi if best_hi is None or hi < best_hi else best_hi
        N += kstar
    require(cands, 'no whole-hosted vertex placement')
    cands.sort(key=lambda t: t[0])
    hi, lo, nstar, chosen, part = cands[0]
    require(all(hi < other[1] for other in cands[1:]), 'optimal placement not certified unique')
    idle_units = {cap: [] for cap in cl}
    idle_units[capstar] += [kstar] * nstar
    for cap, n in chosen.items():
        idle_units[cap] += [cl[cap]['umax']] * n
    if part:
        idle_units[part[0]].append(part[1])
    # children per replica
    idle = Counter()
    for cap, c in cl.items():
        ks = idle_units[cap]
        for k in ks:
            idle[c['rmin'] + 8 * k] += 1
        if c['rmin']:
            idle[c['rmin']] += c['copies'] - len(ks)
    idle.pop(0, None)
    require(sum(r * n for r, n in idle.items()) == sum(c['copies'] * cap for cap, c in cl.items()) - 8 * L * R,
            'idle mass = pending capacity - hosted residual mass')
    ok = None
    for U in _distribute(tpl, v, cl, idle_units):
        flow, hosted = _maxflow({s: R for s in range(L)}, U, {i: w[2] for i, w in tpl['windows'].items()})
        if flow == L * R:
            ok = U
            break
    require(ok is not None, 'window flow cannot host every residual for the optimal placement (not handled)')
    info.update(best_per_unit_option=f'capacity {capstar} fully idle ({kstar} units)', candidates_compared=len(cands),
                fully_idle_best=nstar, other_fully_idle={str(k): n for k, n in sorted(chosen.items())},
                partial=None if not part else f'capacity {part[0]}, {part[1]} unused units',
                used_units_by_slot_index={str(i): u for i, u in sorted(ok.items())}, window_flow='saturates L*R')
    return +idle, info


def banked_idle(L, v, R):
    """Hosting wall violated: every slot fully used (minimal remainders), the overflow residuals of each stage go to
    exact width-m banks (PR510/PR443 rule); needs m = 64 (8 residuals per bank)."""
    tpl = template(L)
    m, T = tpl['m'], tpl['T']
    require(m % 8 == 0, 'exact width-8 bank tiling needs 8 | m')
    cl = _classes(tpl, v)
    U = {i: 2 * v * cl[r]['umax'] for i, (p, r, st) in tpl['windows'].items()}
    flow, hosted = _maxflow({s: R for s in range(L)}, U, {i: w[2] for i, w in tpl['windows'].items()})
    require(flow == sum(U.values()), 'every slot unit is used')
    banks = 0
    for s in range(L):
        over = T * (R - hosted[s]) * 8
        require(over % m == 0, 'per-stage bank tiling')
        banks += over // m
    idle = Counter()
    for cap, c in cl.items():
        if c['rmin']:
            idle[c['rmin']] += c['copies']
    return +idle, dict(banks=banks, overflow_residuals_per_replica=L * R - flow,
                       hosted_per_stage_per_replica={str(s): hosted[s] for s in range(L)})


# --------------------------------------------------------------------------------------------- the PR589 word
_WORD = {}


def word_data():
    if _WORD:
        return _WORD
    w = WLIB.load(_path('word589'))
    exp = _json('expected589')['word']
    F = WLIB.Frames(w)
    V, R = w['v'], w['R']
    N = 2 * V + R
    dim, mask = F.dim, F.mask
    cur = list(w['start'])
    per = [[] for _ in range(N)]

    def climb(r, f):
        a = cur[r]
        if a == f:
            return
        require(mask[a] & mask[f] == mask[a], 'frames nest')
        if dim[f] > dim[a]:
            per[r].append(dim[f] - dim[a])
        cur[r] = f

    def gates(sec):
        for f, t, ss in w[sec]:
            for r in [t, *ss]:
                climb(r, f)
    gates('D')
    gates('A')
    tops = [dim[cur[q]] for q in w['ret']]
    gates('B')
    gates('C')
    for r, f in enumerate(w['final']):
        climb(r, f)
    H0, tops0 = WLIB.replay(w, F)        # exact F2 endpoint replay of tune/wlib.py
    require(Counter(x for p in per for x in p) == H0 and tops == tops0, 'per-register climbs equal wlib.replay')
    local = Counter(H0) + Counter(tops)
    require({str(k): n for k, n in sorted(local.items())} == exp['local_histogram'], 'local paid profile = PR589 record')
    require(tops == [7] * 9 and sum(tops) == exp['decoder_constant'] == 63, 'nine COPY ranks of 7')
    require(all(sum(per[t]) == 7 and sum(per[V + t]) == 7 for t in range(V)), 'each live line: x and y climb 7 each')
    require(all(sum(per[h]) == 8 for h in range(2 * V, N)), 'each helper climbs 8')
    require(sum(r * n for r, n in local.items()) == 8 * R + 14 * V + 63, 'mass 8R + 14v + cst')
    avg = Counter()
    for t in range(V):
        for x in per[t] + per[V + t]:
            avg[x] += 1
    _WORD.update(w=w, V=V, R=R, per=per, local=local, ports_geom=list(w['ports_geom']),
                 avg={r: Q(n, V) for r, n in avg.items()}, punctured=list(w['punctured']))
    return _WORD


def port_of_vector(vec):
    wd = word_data()
    sgn = lambda x: tuple(x) if next(a for a in x if a) > 0 else tuple(-a for a in x)
    hits = [t for t, l in enumerate(wd['w']['lines']) if sgn(l) == sgn(vec)]
    require(len(hits) == 1, f'{vec} is not exactly one live line of the PR589 word')
    return hits[0]


# --------------------------------------------------------------------------------------------- pricing
def _local_profile(dead_ports, cost6, uniform_j=None):
    wd = word_data()
    loc = Counter({r: Q(n) for r, n in wd['local'].items()})
    if uniform_j is None:
        for t in dead_ports:
            for x in wd['per'][t] + wd['per'][wd['V'] + t]:
                loc[x] -= 1
        j = len(dead_ports)
    else:
        j = uniform_j
        for r, a in wd['avg'].items():
            loc[r] -= j * a
    require(loc[7] >= cost6, 'enough rank-7 COPY children')
    loc[7] -= cost6
    loc[6] += cost6
    require(all(n >= 0 for n in loc.values()), 'negative count in the transplanted profile')
    loc = {r: n for r, n in sorted(loc.items()) if n}
    v, cst = wd['V'] - j, 63 - cost6
    require(sum(r * n for r, n in loc.items()) == 8 * wd['R'] + 14 * v + cst, 'local mass 8R + 14v + cst')
    return loc, j, v, cst


def _local_profile_swap(readers, dead, cost6):
    """'transplant-swap' proxy for a hypothetical word whose punctured reader set is `readers` (nine geometry lines)
    and whose dead (punctured) live root duals are `dead` (geometry lines, disjoint from readers).  Starting from the
    PR589 local profile: every line that is live in PR589 but punctured in the hypothetical word (readers or dead
    lines outside the shipped puncture) loses its own PR589 x/y climbs; every shipped punctured line that is live in
    the hypothetical word gains the AVERAGE (x, y) climb pattern (no PR589 record exists for it).  Net: j = |dead|
    patterns removed.  readers = shipped P reproduces the plain transplant exactly."""
    wd = word_data()
    S = set(wd['punctured'])
    gone = [g for g in list(readers) + list(dead) if g not in S]
    added = [g for g in sorted(S) if g not in readers and g not in dead]
    j = len(dead)
    require(len(gone) - len(added) == j, 'line bookkeeping: |gone| - |added| = j')
    loc = Counter({r: Q(n) for r, n in wd['local'].items()})
    for g in gone:
        t = wd['ports_geom'].index(g)
        for x in wd['per'][t] + wd['per'][wd['V'] + t]:
            loc[x] -= 1
    for r, a in wd['avg'].items():
        loc[r] += len(added) * a
    require(loc[7] >= cost6, 'enough rank-7 COPY children')
    loc[7] -= cost6
    loc[6] += cost6
    require(all(n >= 0 for n in loc.values()), 'negative count in the transplanted profile')
    loc = {r: n for r, n in sorted(loc.items()) if n}
    v, cst = wd['V'] - j, 63 - cost6
    require(sum(r * n for r, n in loc.items()) == 8 * wd['R'] + 14 * v + cst, 'local mass 8R + 14v + cst')
    return loc, j, v, cst, dict(removed_pr589_lines=sorted(gone), average_pattern_lines=added)


def price_profile(local, v, R, cst, L, c_start=None):
    """global profile = calls*local + T*idle (slot-model optimum or minimal banks); certified c."""
    tpl = template(L)
    m, T = tpl['m'], tpl['T']
    calls = L * T
    W = live_stock(tpl, v)
    hostable = R * 1 <= tpl['wall_ratio'] * v
    idle, info = idle_optimum(L, v, R, c_start or C_PR589_9) if hostable else (None, None)
    hostable = idle is not None
    out = dict(L=L, m=m, T=T, K=tpl['K'], calls=calls, v=v, R=R, cst=cst,
               wall=f'R <= {qstr(tpl["wall_ratio"])} v = {qstr(tpl["wall_ratio"] * v)} (aggregate Hall bound of the windows)',
               R_max_whole_hosting=int(tpl['wall_ratio'] * v))

    def assemble(idle_rep, Wl):
        P = Counter()
        for r, n in local.items():
            P[r] += calls * n
        for r, n in idle_rep.items():
            P[r] += T * n
        P = {r: n for r, n in sorted(P.items()) if n}
        mass = sum(r * n for r, n in P.items())
        require(m * Wl - mass == deficit(tpl, v, cst), 'rank-mass identity M*live - mass = T(2Kv - L cst)')
        require(2 * max(P) ** tpl['halving_depth'] < m ** tpl['halving_depth'], 'halving guard')
        return P

    if hostable:
        # iterate until the placement is certified optimal at c_hat = c + 10^-24
        seen = []
        for _ in range(6):
            P = assemble(idle, W)
            c = certify(P, m, W)
            seen.append(c)
            idle2, info2 = idle_optimum(L, v, R, c + GRID)
            if idle2 == idle:
                info = info2
                break
            idle = idle2
        else:
            raise AssertionError('placement optimisation did not stabilise')
        out.update(hostable=True, W=W, pricing_mode='whole-hosted, slot-model optimum (certified at c + 1e-24)',
                   hosting=info, idle_per_replica=idle)
    else:
        idle, binfo = banked_idle(L, v, R)
        Wb = W + binfo['banks']
        P = assemble(idle, Wb)
        c = certify(P, m, Wb)
        cl = _classes(tpl, v)
        out.update(hostable=False, W=Wb, W_whole=W,
                   pricing_mode='IF HOSTED IN BANKS (hypothetical): hosting wall violated; overflow residuals in exact '
                                'width-64 banks (PR510/PR443 rule), live stock +banks; minimal banks, not optimised',
                   hosting=dict(slack_units_per_replica=sum(c_['copies'] * c_['umax'] for c_ in cl.values()) - L * R,
                                **binfo),
                   idle_per_replica=idle)
    out['rem'] = {r: T * n for r, n in sorted(out['idle_per_replica'].items())}
    out['profile'] = P
    out['deficit'] = deficit(tpl, v, cst)
    out['c'] = c
    return out


def _finish(res, local, extra):
    c = res['c']
    res.update(extra)
    res['local_profile'] = {str(r): qstr(n) for r, n in local.items()}
    res['profile'] = {str(r): qstr(n) for r, n in res['profile'].items()}
    res['rem'] = {str(r): n for r, n in res['rem'].items()}
    res['idle_per_replica'] = {str(r): n for r, n in sorted(res['idle_per_replica'].items())}
    res['c_exact'] = qstr(c)
    res['c_decimal'] = dec(c)
    res['gain_vs_selected_pct'] = dec(100 * (c - C_PR589_9) / C_PR589_9, 6)
    return res


def price(dead_lines, cost6, L, *, index='geom', variant='transplant', R=R0, readers=None, helper_model=None):
    """dead_lines: live lines of the PR589 word to puncture (geometry indices 0..119 as in the word's 'punctured'
    field, or live port indices 0..110 with index='port').  cost6: retained totals of COPY rank 6 (<= 9, <= j).
    variant 'uniform' ignores which lines are given and removes j average (x, y) climb patterns.
    readers (geometry indices, nine distinct lines): price a hypothetical word whose punctured reader set is
    `readers` instead of the shipped P ('transplant-swap', see _local_profile_swap); dead lines may then be shipped
    punctured lines.  R must equal the word's helper count (helper climbs are not transplanted)."""
    wd = word_data()
    require(helper_model in (None, 'average-helper'), "helper_model is None or 'average-helper'")
    require(R == wd['R'] or helper_model == 'average-helper',
            f"R = {R}: only the word's own helper count {wd['R']} is consistent with the transplanted "
            "local profile (a different R would break the rank-mass identity; see helper_model='average-helper')")
    require(index in ('geom', 'port'), "index is 'geom' or 'port'")
    if readers is not None:
        require(index == 'geom' and variant == 'transplant', "readers needs index='geom' and variant='transplant'")
        rd, dd = [int(x) for x in readers], [int(x) for x in dead_lines]
        require(len(rd) == 9 == len(set(rd)) and all(0 <= g < 120 for g in rd), 'readers: nine distinct lines 0..119')
        require(len(dd) == len(set(dd)) and all(0 <= g < 120 for g in dd), 'dead lines: distinct lines 0..119')
        require(not set(rd) & set(dd), 'dead lines must be live (not readers)')
        require(0 <= cost6 <= min(9, len(dd)), 'cost6 must satisfy 0 <= cost6 <= min(9, j)')
        local, j, v, cst, book = _local_profile_swap(rd, dd, cost6)
        local = _helper_shift(local, R, v, cst) if helper_model else local
        res = price_profile(local, v, R, cst, L)
        return _finish(res, local, dict(variant='transplant-swap', j=j, cost6=cost6, readers_geom=sorted(rd),
                                        dead_ports=[wd['ports_geom'].index(g) if g in wd['ports_geom'] else None
                                                    for g in dd],
                                        dead_lines_geom=dd, swap_bookkeeping=book))
    if index == 'geom':
        bad = [g for g in dead_lines if g not in wd['ports_geom']]
        require(not bad, f'not live lines of the PR589 word: {bad}')
        ports = [wd['ports_geom'].index(g) for g in dead_lines]
    else:
        ports = list(dead_lines)
        require(all(0 <= t < wd['V'] for t in ports), 'port out of range')
    require(len(set(ports)) == len(ports), 'dead lines must be distinct')
    require(0 <= cost6 <= min(9, len(ports)), 'cost6 must satisfy 0 <= cost6 <= min(9, j)')
    require(variant in ('transplant', 'uniform'), 'variant')
    if variant == 'uniform':
        return price_uniform(len(ports), cost6, L, R=R)
    require(variant == 'transplant' or not helper_model, "helper_model needs variant='transplant'")
    local, j, v, cst = _local_profile(ports, cost6)
    local = _helper_shift(local, R, v, cst) if helper_model else local
    res = price_profile(local, v, R, cst, L)
    return _finish(res, local, dict(variant='transplant', j=j, cost6=cost6, dead_ports=ports,
                                    dead_lines_geom=[wd['ports_geom'][t] for t in ports]))


def _helper_shift(local, R, v, cst):
    """helper_model='average-helper' (opt-in; the default refuses R != the word's R): a word with R helpers instead of
    the PR589 word's R0 has its local profile shifted by (R - R0) copies of the AVERAGE helper climb pattern of the
    PR589 word (mean over its R0 helper registers of their paid climbs; rank mass 8 per helper), so the local mass is
    8R + 14v + cst.  A hypothesis for the extra carriers / junk wires of a different reader set (carriers.py), not a
    replay of any word."""
    wd = word_data()
    V, R0 = wd['V'], wd['R']
    hav = Counter()
    for h in range(2 * V, 2 * V + R0):
        for x in wd['per'][h]:
            hav[x] += 1
    require(sum(r * n for r, n in hav.items()) == 8 * R0, 'PR589 helper climbs have rank mass 8 per helper')
    loc = Counter(local)
    for r, n in hav.items():
        loc[r] += (R - R0) * Q(n, R0)
    require(all(n >= 0 for n in loc.values()), 'negative count after the helper shift')
    loc = {r: n for r, n in sorted(loc.items()) if n}
    require(sum(r * n for r, n in loc.items()) == 8 * R + 14 * v + cst, 'local mass 8R + 14v + cst after the shift')
    return loc


def price_uniform(j, cost6, L, *, R=R0):
    require(R == word_data()['R'], f"R = {R}: only the word's own helper count is consistent with the local profile")
    require(0 <= j <= 9 and 0 <= cost6 <= j, 'uniform variant: 0 <= cost6 <= j <= 9')
    local, j, v, cst = _local_profile([], cost6, uniform_j=j)
    res = price_profile(local, v, R, cst, L)
    return _finish(res, local, dict(variant='uniform', j=j, cost6=cost6, dead_ports=None, dead_lines_geom=None))


# --------------------------------------------------------------------------------------------- controls
def _rem_from_selection(L, key):
    tpl = template(L)
    sel = _json(key)['bit']
    copies = Counter()
    rem = Counter()
    for i, pat, n in sel['patterns']:
        cap = tpl['windows'][i][1]
        require(all(w == 8 for w in pat) and sum(pat) <= cap, 'pattern fits its slot capacity')
        copies[i] += n
        if cap - sum(pat):
            rem[cap - sum(pat)] += n
    require(set(copies) == set(tpl['windows']), 'the frozen selection covers exactly the template windows')
    per = set(copies.values())
    require(len(per) == 1, 'equal copy counts per slot index')
    scale = tpl['T'] if per == {2 * 111} else 1   # nine-stage files count per replica, eleven-stage over all replicas
    require(per.pop() * scale == 2 * 111 * tpl['T'], 'copies = 2v per replica')
    for i, w, s, n in sel['stages']:
        require(s in tpl['windows'][i][2], 'every frozen residual stage lies in its slot window')
    return {r: n * scale for r, n in sorted(rem.items())}


def _rem_from_record(record, L, local):
    tpl = template(L)
    calls = L * tpl['T']
    idle = Counter({int(r): n for r, n in record['profile'].items()})
    idle.subtract(Counter({int(r): calls * n for r, n in local.items()}))
    return {r: n for r, n in sorted(idle.items()) if n}


def controls():
    checks = []

    def ok(name, cond):
        require(cond, f'control failed: {name}')
        checks.append(name)
    e589, e555 = _json('expected589'), _json('expected555')
    loc589 = {int(r): n for r, n in e589['word']['local_histogram'].items()}
    loc555 = {int(r): n for r, n in e555['word']['local_histogram'].items()}
    out = {}
    # control 1: nine stages, PR589
    t9 = template(9)
    ok('nine-stage capacities {14,7,28,7,42,7,42,28,14}', t9['capacities'] == [14, 7, 28, 7, 42, 7, 42, 28, 14])
    ok('nine-stage wall R <= 4v', t9['wall_ratio'] == 4)
    rem_rec = _rem_from_record(e589['nine'], 9, loc589)
    rem_sel = _rem_from_selection(9, 'selection9')
    idle_opt, _ = idle_optimum(9, 111, R0, C_PR589_9 + GRID)
    rem_opt = {r: t9['T'] * n for r, n in sorted(idle_opt.items())}
    ok('REM9: record = frozen selection = slot-model optimum = fastc.py REM',
       rem_rec == rem_sel == rem_opt == REM9_PINNED)
    r1 = price([], 0, 9)
    ok('control 1: PR589 nine-stage c reproduced exactly',
       Q(r1['c_exact']) == C_PR589_9 == Q(e589['nine']['bit_lower']) and r1['hostable'])
    ok('PR589 nine-stage profile = record', r1['profile'] == {k: str(v) for k, v in e589['nine']['profile'].items()})
    out['control1'] = dict(c=r1['c_exact'], rem=r1['rem'])
    # control 2: eleven stages, PR555 untuned word
    t11 = template(11)
    ok('eleven-stage capacities {14,7,28,7,42,7,56,7,56,42,28,14}',
       t11['capacities'] == [14, 7, 28, 7, 42, 7, 56, 7, 56, 42, 28, 14])
    ok('eleven-stage wall 11R <= 64v', t11['wall_ratio'] == Q(64, 11))
    ok('eleven-stage live 8880 = 80v', live_stock(t11, 111) == 8880 == e555['eleven']['bit']['live'])
    rem11_rec = _rem_from_record(e555['eleven'], 11, loc555)
    rem11_rec589 = _rem_from_record(e589['eleven'], 11, loc589)
    rem11_sel = _rem_from_selection(11, 'hosting11')
    P555 = Counter({r: 88 * n for r, n in loc555.items()})
    P555.update(rem11_rec)
    c555_11 = certify(P555, 78, 8880)
    res555 = price_profile({r: Q(n) for r, n in loc555.items()}, 111, R0, 63, 11)
    ok('REM11: PR555 record = PR589 record = frozen selection = slot-model optimum',
       rem11_rec == rem11_rec589 == rem11_sel == res555['rem'] == {2: 3552, 4: 3552, 6: 3552, 7: 7104, 56: 2600})
    ok('control 2: PR555 eleven-stage c reproduced exactly',
       c555_11 == res555['c'] == C_PR555_11 == Q(e555['eleven']['bit_lower']))
    ok('eleven-stage deficit 3336 = 8(10v - 11 cst)', deficit(t11, 111, 63) == 3336)
    out['control2'] = dict(c=qstr(res555['c']), rem={str(k): v for k, v in res555['rem'].items()})
    # cross-checks
    r11 = price([], 0, 11)
    ok('PR589 eleven-stage c (tune/EXPECTED.json) reproduced', Q(r11['c_exact']) == C_PR589_11 == Q(e589['eleven']['bit_lower']))
    res555_9 = price_profile({r: Q(n) for r, n in loc555.items()}, 111, R0, 63, 9)
    ok('PR555 nine-stage c reproduced', res555_9['c'] == C_PR555_9 == Q(e555['nine']['bit_lower']))
    ok('rational certify path (used for fractional profiles) agrees with the engine on both controls',
       certify({int(r): Q(n) for r, n in r1['profile'].items()}, 64, 28416, rational_path=True) == C_PR589_9
       and certify(P555, 78, 8880, rational_path=True) == C_PR555_11)
    ok('uniform j = 0 equals transplant j = 0 at both L',
       price_uniform(0, 0, 9)['c_exact'] == r1['c_exact'] and price_uniform(0, 0, 11)['c_exact'] == r11['c_exact'])
    shipped = sorted(word_data()['punctured'])
    ok('transplant-swap with readers = shipped P equals the plain transplant (P110 at L = 9)',
       price([87], 1, 9, readers=shipped)['c_exact'] == price([87], 1, 9)['c_exact'])
    # negative controls
    for name, fn in [('c + 1e-24 rejected by the engine', lambda: ENGINE.moment(
                         {int(k): v for k, v in e589['nine']['profile'].items()}, 64, 28416, C_PR589_9 + GRID, True)[0] > 1),
                     ('R = 445 > 4v at v = 111 is not whole-hostable', lambda: idle_optimum(9, 111, 445, C_PR589_9)[0] is None),
                     ('R = 444 = 4v at v = 111 is hostable with zero slack',
                      lambda: idle_optimum(9, 111, 444, C_PR589_9)[1]['slack_units_per_replica'] == 0)]:
        ok(name, fn())
    for name, fn in [('a punctured line cannot be a dead line', lambda: price([10], 0, 9)),
                     ('cost6 > j refused', lambda: price([87], 2, 9)),
                     ('R other than the word helper count refused', lambda: price([], 0, 9, R=445)),
                     ('a dead line inside the reader set refused',
                      lambda: price([87], 1, 9, readers=[87] + sorted(word_data()['punctured'])[1:])),
                     ('moved REM unit breaks the rank-mass identity', lambda: _mass_break())]:
        try:
            fn()
        except AssertionError:
            checks.append(name)
        else:
            raise AssertionError(f'negative control accepted: {name}')
    out['checks'] = checks
    return out


def _mass_break():
    tpl = template(9)
    P = Counter({r: 288 * n for r, n in word_data()['local'].items()})
    P.update({2: 13920 - 32, 4: 14208 + 32, 6: 14208, 7: 21312, 42: 288})
    require(64 * 28416 - sum(r * n for r, n in P.items()) == deficit(tpl, 111, 63), 'rank-mass identity')


# --------------------------------------------------------------------------------------------- CLI
def dual_root_line():
    res = _json('pr1084')['shipped']
    a, b = res['dual_root']['a'], res['dual_root']['b']
    wd = word_data()
    t = port_of_vector(b)
    ip = lambda x, y: sum(p * q for p, q in zip(x, y))
    P = res['punctured']
    require(len(P) == 9 and a in P, 'a is a shipped punctured line')
    require(all(((1 + ip(p, b) // 2) % 2) == (1 if p == a else 0) for p in P), 'b is the F2 dual of a (B0 = delta)')
    return t, wd['ports_geom'][t], a, b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--json', type=Path, default=None, help='write all rows to this JSON file')
    a = ap.parse_args(argv)
    require(__debug__, 'run without -O: the pinned engines signal rejection with assert')
    ctrl = controls()
    port_b, geom_b, va, vb = dual_root_line()
    rows = []

    def row(label, r):
        r = dict(r, label=label)
        rows.append(r)
        flag = '' if r['hostable'] else '  [NOT HOSTABLE: c IF HOSTED IN BANKS]'
        print(f"{label:28s} L={r['L']:2d} v={r['v']:3d} R={r['R']} cst={r['cst']:2d} hostable={str(r['hostable']):5s} "
              f"c={r['c_decimal']}  gain vs selected {r['gain_vs_selected_pct']:>11s}%  idle/rep {r['idle_per_replica']}{flag}")
    print(f'controls: PR589 nine-stage c {dec(C_PR589_9)}; PR555 eleven-stage c {dec(C_PR555_11)} (both exact)')
    print(f'dual root b = {vb} (PR1084 RESULTS.json shipped.dual_root.b) = live port {port_b} = geometry line {geom_b}; '
          f'reader a = {va}')
    for L in (9, 11):
        row(f'P111@{L} (transplant j=0)', price([], 0, L))
    for L in (9, 11):
        row(f'P110@{L} (dead b={geom_b}, cost6=1)', price([geom_b], 1, L))
    for L in (9, 11):
        for j in range(10):
            row(f'uniform j={j} cost6={j} @{L}', price_uniform(j, j, L))
    by = {(r['label']): r for r in rows}
    require(by['P111@9 (transplant j=0)']['c_exact'] == qstr(C_PR589_9), 'P111@9 control')
    require(by['P111@11 (transplant j=0)']['c_exact'] == qstr(C_PR589_11), 'P111@11 control')
    if a.json:
        a.json.write_text(json.dumps(dict(controls=ctrl, rows=rows), indent=1, sort_keys=True, default=str) + '\n')
    nh9 = sum(1 for r in rows if r['L'] == 9 and not r['hostable'])
    p110 = by[f'P110@9 (dead b={geom_b}, cost6=1)']
    print(f"PASS_BIT_STAGE_PRICER controls=2 checks={len(ctrl['checks'])} rows={len(rows)} "
          f"P110@9 c={p110['c_exact']} hostable={p110['hostable']} nine-stage-unhostable={nh9}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f'FAIL_BIT_STAGE_PRICER {exc}')
        sys.exit(1)
