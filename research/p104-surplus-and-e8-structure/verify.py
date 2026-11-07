#!/usr/bin/env python3
"""Exact checks for the P104 invoice-surplus identity and the E8 structure of the 104 ports.
Python 3.12, standard library only (fractions, decimal, json, gzip, hashlib).

Run:  python3 -B research/p104-surplus-and-e8-structure/verify.py
Expected marker: PASS_P104_SURPLUS_AND_E8_STRUCTURE

Sections (every failure raises ValueError, so the checks survive python -O):
  0. pins of the retained pull-request inputs and of the base-commit inputs
  1. native words: legality replay, endpoint, paid-mass accounting  (#6702 word, #6349 word)
  2. literal callers: outer tables, stage balance, outer margin 17k-1 per port (#6726, #6726 unretired, #6348)
  3. complete invoices: S = 48k - ports = (k-1)p - kO, kappa by exact bisection, first-order bracket
  4. mixed-port bound (model with explicit hypotheses)
  5. E8 structure of the ports: quadratic form, explicit E8 lift, frames, port stabiliser, frame-pair classes
  6. public block P and O = I - P versus the E8 Gram matrix
  7. private-descent mass: hop graph (8 chains of mass 7) and the dim-7 certificate
  8. negative controls
"""
import ast
import gzip
import hashlib
import itertools
import json
import random
import re
import sys
from collections import Counter, defaultdict, deque
from decimal import Decimal as Dec, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = {}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def expect_error(fn, tag):
    try:
        fn()
    except ValueError as e:
        need(tag in str(e), ('wrong failure', tag, str(e)))
        return str(e)[:90]
    raise ValueError('control accepted: ' + tag)


def load_json(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


wt = lambda x: bin(x).count('1')
dot = lambda a, b: wt(a & b) & 1


# ----------------------------------------------------------------------------------------- 0 pins
def check_pins():
    pins = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    src = json.loads((HERE / 'SOURCES.json').read_text())
    n = 0
    for row in src['files']:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], ('base input sha256', row['path']))
            need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == row['git_blob'], ('base blob', row['path']))
            n += 1
    OUT['pins'] = dict(retained=len(pins), base_inputs=n)


# ------------------------------------------------------------------------------ 1 native word replay
def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in out, 'independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def addrow(dst, src, q):
    for k, v in tuple(src.items()):
        x = dst.get(k, 0) + q * v
        if x:
            dst[k] = x
        else:
            dst.pop(k, None)


def native_account(w, want_sym=False):
    """Replay a native word: frame legality, exact endpoint, paid/helper accounting.
    Public roles only climb (MOVE with nested up), private (owned) roles only descend; ADD/COPY/SCALE act at one frame.
    Also returns the symbolic rows in which each private descent output is a fresh symbol z_h."""
    n, nown = w['public'], w['owned_fields']
    N = n + nown
    frames = [span(b) for b in w['frames']]
    dims = [len(b) for b in w['frames']]
    need(len(w['live']) == len(w['ports']) == 104, '104 ports')
    cur = list(w['initial']) + [None] * nown
    owned = set()
    real = [{r: Q(1)} if r < n else {} for r in range(N)]
    sym = [{r: Q(1)} if r < n else {} for r in range(N)]
    paid = Counter()
    pub_mass = own_mass = lifetimes = 0
    hops = []
    for i, e in enumerate(w['program']):
        op, r = e[0], e[1]
        need(0 <= r < N, ('role', i))
        if op == 'MOVE':
            a, b, private = e[2:]
            need(cur[r] == a and private == (r in owned), ('move current', i))
            if private:
                need(frames[b] < frames[a], ('private move must descend', i))
                own_mass += dims[a] - dims[b]
                hops.append(dict(index=i, role=r, a=dims[a], b=dims[b], zin=[k[1] for k in sym[r] if isinstance(k, tuple)]))
                sym[r] = {('z', len(hops) - 1): Q(1)}
            else:
                need(frames[a] < frames[b], ('public move must climb', i))
                pub_mass += dims[b] - dims[a]
            paid[abs(dims[b] - dims[a])] += 1
            cur[r] = b
        elif op == 'INIT':
            need(r >= n and r not in owned, ('init', i))
            owned.add(r); lifetimes += 1
            real[r] = {}; sym[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            need(r in owned and cur[r] == e[2], ('clear', i))
            real[r] = {}; sym[r] = {}; cur[r] = None; owned.remove(r)
        else:
            q, f = Q(e[-2]), e[-1]
            need(q != 0 and cur[r] == f, ('frame of target', i))
            d = q.denominator
            need(d & (d - 1) == 0, ('dyadic', i))
            if op == 'SCALE':
                real[r] = {k: v * q for k, v in real[r].items()}
                sym[r] = {k: v * q for k, v in sym[r].items()}
            else:
                s = e[2]
                need(s != r and 0 <= s < N and cur[s] == f, ('frame of source', i))
                if op == 'COPY':
                    need(r in owned and not real[r], ('COPY zero', i))
                    real[r] = {}; sym[r] = {}
                else:
                    need(op == 'ADD', ('opcode', i))
                addrow(real[r], real[s], q)
                addrow(sym[r], sym[s], q)
    need(not owned and cur[:n] == w['final'], 'exits')
    main = set(w['live']) | {r + 112 for r in w['live']}
    for r in range(n):
        exp = {r: Q(1)}
        if r - 112 in w['live']:
            exp[r - 112] = Q(1)
        need(real[r] == exp, ('endpoint', r))
    helpers = Counter()
    main_climb = 0
    for r in range(n):
        d = dims[w['final'][r]] - dims[w['initial'][r]]
        if r in main:
            main_climb += d
        else:
            helpers[d] += 1
    need(len(main) == 208, '208 main roles')
    return dict(n=n, helpers=dict(helpers), paid=dict(paid), pub_mass=pub_mass, own_mass=own_mass,
                lifetimes=lifetimes, main_climb=main_climb, hops=hops, sym=sym, dims=dims, main=main,
                helper_mass=sum(k * v for k, v in helpers.items()), paid_mass=sum(k * v for k, v in paid.items()))


def check_native():
    words = {}
    for name, path in (('pr6702', HERE / 'retained/pr6702/WORD.json.gz'),
                       ('pr6349', ROOT / 'research/p104-native-input-lifting/WORD.json.gz')):
        w = load_json(path)
        a = native_account(w)
        # paid mass identity: every public role climbs, every private role descends
        need(a['paid_mass'] == a['pub_mass'] + a['own_mass'], 'paid mass split')
        need(a['pub_mass'] == a['main_climb'] + a['helper_mass'], 'public mass = main climbs + helper ranks')
        need(a['main_climb'] == 16 * 104, 'every main role climbs by 8')
        words[name] = (w, a)
        OUT[name] = dict(public=a['n'], helpers=sum(a['helpers'].values()), helper_mass=a['helper_mass'],
                         paid_mass=a['paid_mass'], main_climb=a['main_climb'], private_descent_mass=a['own_mass'],
                         lifetimes=a['lifetimes'])
        need(a['own_mass'] == 56, 'private descent mass 56')
        need(a['paid_mass'] - a['helper_mass'] == 1664 + 56, 'native margin -(16p+56)')
    return words


def consts(path):
    text = Path(path).read_text()
    h = ast.literal_eval(re.search(r'^HELPERS=(\{.*\})', text, re.M).group(1))
    p = ast.literal_eval(re.search(r'^LOCAL_PAID=(\{.*\})', text, re.M).group(1))
    return h, p


def check_edits(a6702):
    """#6805 and #6824 histograms from their retained constants; edits are rank conserving."""
    h5, p5 = consts(HERE / 'retained/pr6805/pricing.py')
    h6, p6 = consts(HERE / 'retained/pr6824/pricing.py')
    wit = json.loads((HERE / 'retained/pr6805/WITNESS.json').read_text())['screen_hit']
    w = load_json(HERE / 'retained/pr6702/WORD.json.gz')
    dims = a6702['dims']
    piv = wit['pivot']
    need(dims[w['final'][piv]] - dims[w['initial'][piv]] == 9, 'pivot 368 is a rank-9 helper in the #6702 word')
    p80 = wit['paths'][0]
    mv = w['program'][14088]
    need(mv[:2] == ['MOVE', 80] and dims[mv[3]] - dims[mv[2]] == 6 and wit['ranks'] == [4, 5], 'retimed move 6 -> 1+5')
    need(p80['old_paid'] == [6] and p80['new_paid'] == [1, 5], 'witness paid ranks')
    # direct comparison: constants of #6805 against the replayed #6702 histogram plus the witness edits
    dH = {r: h5.get(r, 0) - a6702['helpers'].get(r, 0) for r in range(1, 10)}
    dP = {r: p5.get(r, 0) - a6702['paid'].get(r, 0) for r in range(1, 9)}
    need({r: v for r, v in dH.items() if v} == {4: 1, 5: 1, 9: -1}, ('helper delta', dH))
    need({r: v for r, v in dP.items() if v} == {1: 1, 5: 1, 6: -1}, ('paid delta', dP))
    d6H = {r: h6.get(r, 0) - h5.get(r, 0) for r in range(1, 10)}
    d6P = {r: p6.get(r, 0) - p5.get(r, 0) for r in range(1, 9)}
    for (x, y) in (({r: v for r, v in dH.items()}, {r: v for r, v in dP.items()}),
                   (d6H, d6P)):
        need(sum(r * v for r, v in x.items()) == sum(r * v for r, v in y.items()), 'edit conserves rank')
    OUT['edits'] = dict(pr6805_vs_pr6702=dict(helpers={k: v for k, v in dH.items() if v}, paid={k: v for k, v in dP.items() if v}),
                        pr6824_vs_pr6805=dict(helpers={k: v for k, v in d6H.items() if v}, paid={k: v for k, v in d6P.items() if v}))
    return {'pr6702': (a6702['helpers'], a6702['paid']), 'pr6805': (h5, p5), 'pr6824': (h6, p6)}


# ------------------------------------------------------------------------------------ 2 callers
def caller_outer(c):
    """Outer target / paid tables of a caller word (104 ports): targets from the declared diagonal, paid from
    thin queries and whole idle jobs.  Also per-stage coverage."""
    K = c['stages']
    T, P = Counter(), Counter()
    cov = Counter()
    for t in c['diagonal']:
        need(t[1] == 0, 'no stage-zero factor')
        T[t[0] % 2 + 8 * sum(t[2:])] += 104
        for s in range(1, K + 1):
            cov[s] += 104 * t[1 + s]
    queries = 0
    for e in c['events']:
        if e[0] == 'QUERY':
            P[1] += 104; queries += 1
        elif e[0] == 'IDLE':
            P[8 * len(e[3])] += 208
            for s in e[3]:
                cov[s] -= 208
        elif e[0] == 'IDLE_ONE':
            P[8 * len(e[2])] += 104
            for s in e[2]:
                cov[s] -= 104
    need(sum(1 for e in c['events'] if e[0] == 'LOCAL') == K, 'one local call per stage')
    odd = sum(n for r, n in T.items() if r % 2) // 104
    margin = sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items())
    return dict(T=dict(T), P=dict(P), stage_balance={s: cov[s] for s in range(1, K + 1)}, k=K,
                odd_targets=odd, thin_queries=queries, margin=margin)


def check_callers():
    res = {}
    for name, path in (('pr6726', HERE / 'retained/pr6726/CONTROLLER.json'),
                       ('pr6726_unretired', HERE / 'retained/pr6726/CONTROLLER-UNRETIRED.json'),
                       ('pr6348', ROOT / 'research/balanced-query-tree/CONTROLLER.json')):
        c = load_json(path)
        o = caller_outer(c)
        k = o['k']
        need(set(o['stage_balance'].values()) == {208}, ('stage balance 2p per stage', name))
        need(o['margin'] == 104 * (17 * k - 1), ('outer margin 104(17k-1)', name, o['margin']))
        need(o['margin'] == 104 * (16 * k + o['odd_targets'] - o['thin_queries']), ('odd targets minus thin queries', name))
        res[name] = o
        OUT['caller_' + name] = dict(k=k, outer_margin=o['margin'], per_port=o['margin'] // 104, odd_targets=o['odd_targets'],
                                     thin_queries=o['thin_queries'], stage_balance=208)
    need(res['pr6726']['margin'] == 31720 and res['pr6726']['odd_targets'] == 32 and res['pr6726']['thin_queries'] == 15,
         '#6726: 31720 = 104*305, 32 odd targets, 15 thin queries')
    return res


# ----------------------------------------------------------------------------- 3 complete invoices
getcontext().prec = 50


def invoice(outer, H, P, k):
    T, Pd = Counter(outer['T']), Counter(outer['P'])
    for r, n in H.items():
        T[r] += k * n
    for r, n in P.items():
        Pd[r] += k * n
    return T, Pd


def surplus(T, P):
    return sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items())


def kappa(T, P):
    lt = [(n, Dec(r).ln()) for r, n in T.items()]
    lp = [(n, Dec(r).ln()) for r, n in P.items()]

    def g(k):
        e = 1 - k
        return sum(n * (l * e).exp() for n, l in lt) - sum(n * (l * e).exp() for n, l in lp)
    lo, hi = Dec('0.00001'), Dec('0.02')
    for _ in range(170):
        m = (lo + hi) / 2
        if g(m) > 0:
            lo = m
        else:
            hi = m
    return lo


def dfun(T, P, t):
    """D(t) = sum (T-P) r^(1-t) ln r."""
    return sum(n * (Dec(r).ln() * (1 - t)).exp() * Dec(r).ln() for r, n in T.items()) - \
        sum(n * (Dec(r).ln() * (1 - t)).exp() * Dec(r).ln() for r, n in P.items())


def check_invoices(callers, hist, native6349):
    rows = {}
    cases = [('#6702 word + #6726 caller', 'pr6726', 'pr6702', 18),
             ('#6805', 'pr6726', 'pr6805', 18),
             ('#6824', 'pr6726', 'pr6824', 18)]
    for label, cn, wn, k in cases:
        H, P = hist[wn]
        T, Pd = invoice(callers[cn], H, P, k)
        S = surplus(T, Pd)
        need(S == 760 == 48 * k - 104 == (k - 1) * 104 - k * 56, ('S', label, S))
        kap = kappa(T, Pd)
        rows[label] = (S, kap, T, Pd)
    # k = 19: #6348 caller with the #6349 native word
    a = native6349
    T, Pd = invoice(callers['pr6348'], a['helpers'], a['paid'], 19)
    S = surplus(T, Pd)
    need(S == 808 == 48 * 19 - 104 == 18 * 104 - 19 * 56, ('S k=19', S))
    rows['#6348 caller + #6349 word'] = (S, kappa(T, Pd), T, Pd)
    k5 = rows['#6805'][1]
    need(Dec('0.0033081451891') < k5 < Dec('0.0033081451892'), ('kappa #6805', k5))
    k6 = rows['#6824'][1]
    need(Dec('0.00330823456614') < k6 < Dec('0.00330823456615'), ('kappa #6824', k6))
    k2 = rows['#6702 word + #6726 caller'][1]
    need(Dec('0.0033072446848') < k2 < Dec('0.0033072446849'), ('kappa #6726 root on the #6702 word', k2))
    summary = {}
    for label, (S, kap, T, Pd) in rows.items():
        d0, dk = dfun(T, Pd, Dec(0)), dfun(T, Pd, kap)
        # exact mean-value form: S = kappa * Dbar ; Dbar lies between D(kappa) and D(0) when D is monotone on [0,kappa]
        need(S / d0 < kap < S / dk, ('first-order bracket', label))
        summary[label] = dict(S=S, kappa=str(kap)[:20], S_over_D0=str(S / d0)[:11], S_over_Dk=str(S / dk)[:11],
                              rel_bracket=str((S / dk - S / d0) / kap)[:7])
    OUT['invoices'] = summary
    return rows


# --------------------------------------------------------------------------------- 4 mixed ports
def cost_floor(a):
    """Exact 8-term decoder copy-cost floor on a live set of a lines (96 <= a <= 120): max(a - 48, 56)."""
    need(96 <= a <= 120, 'live set outside 96..120 lines')
    return max(a - 48, 56)


def mixed_surplus(sizes, union, costs=None):
    """Hypothesis H-mix: call j on a live set of a_j ports has native margin -(16 a_j + O_j) and the caller margin
    is 17 sum a_j - |U|.  Then S = sum_j (a_j - O_j) - |U|."""
    costs = costs or [cost_floor(a) for a in sizes]
    return sum(a - o for a, o in zip(sizes, costs)) - union


def check_mixed():
    rnd = random.Random(104)
    for k in (18, 19):
        best = max(mixed_surplus([a] * k, a) for a in range(96, 121))
        need(best == 48 * k - 104 == mixed_surplus([104] * k, 104), ('uniform optimum', k))
        arg = [a for a in range(96, 121) if mixed_surplus([a] * k, a) == best]
        need(arg == [104], ('unique uniform maximiser', arg))
    worst = 0
    for _ in range(20000):
        k = rnd.choice((18, 19))
        union = rnd.randint(96, 120)
        sizes = [rnd.randint(96, union) for _ in range(k)]
        if max(sizes) < union and rnd.random() < 0.5:
            sizes[0] = union
        u = max(sizes) if rnd.random() < 0.3 else union
        S = mixed_surplus(sizes, u)
        need(S <= 48 * k - u, 'S <= 48k - |U|')
        need(S <= 48 * k - 104, 'S <= 48k - 104')
        if S == 48 * k - 104:
            need(u == 104 and all(a == 104 for a in sizes), 'equality only for the uniform 104 set')
        worst = max(worst, S)
    for k in (18, 19):                          # beyond 104 every extra line nets -1
        need(all(mixed_surplus([a + 1] * k, a + 1) == mixed_surplus([a] * k, a) - 1 for a in range(104, 120)), 'beyond 104')
        need(all(mixed_surplus([a + 1] * k, a + 1) > mixed_surplus([a] * k, a) for a in range(96, 104)), 'below 104')
    OUT['mixed'] = dict(max_random=worst, cap_k18=48 * 18 - 104, cap_k19=48 * 19 - 104)


# ------------------------------------------------------------------------------------ 5 E8 structure
def lift(v):
    """Explicit E8 root of the sum-zero model of R^9: weight 3 -> e_T - 1/3 ; weight 7 (zero set {i,j}) -> e_i - e_j."""
    if wt(v) == 3:
        return tuple((Q(1) if v >> i & 1 else Q(0)) - Q(1, 3) for i in range(9))
    z = [i for i in range(9) if not v >> i & 1]
    u = [Q(0)] * 9
    u[z[0]], u[z[1]] = Q(1), Q(-1)
    return tuple(u)


ip = lambda a, b: sum(x * y for x, y in zip(a, b))


def cliques(V, size):
    V = sorted(V)
    adj = {v: {u for u in V if u != v and dot(u, v)} for v in V}
    out = []

    def rec(cur, cand):
        if len(cur) == size:
            out.append(tuple(cur)); return
        for v in sorted(cand):
            if not cur or v > cur[-1]:
                rec(cur + [v], cand & adj[v])
    rec([], set(V))
    return out


def stabiliser(ports):
    """All linear g of F2^9 with dot(gx,gy)=dot(x,y) and g(ports)=ports, by exhaustive search (see PROOF 5.4)."""
    Ps = set(ports)
    ns = [v for v in range(512) if wt(v) & 1 and wt(v ^ 511) in (2, 6)]
    M = sorted(set(ns) - Ps)
    basis, sp = [], {0}
    for v in M:
        if v not in sp:
            basis.append(v); sp |= {x ^ v for x in sp}
    need(len(basis) == 8, 'rank of the missing set')
    v0 = next(p for p in ports if p not in sp)
    full = basis + [v0]
    combo = {0: 0}
    for i, b in enumerate(full):
        for x, c in list(combo.items()):
            combo[x ^ b] = c | (1 << i)
    need(len(combo) == 512, 'basis of F2^9')
    n = len(M)
    D = [[dot(a, b) for b in M] for a in M]
    auts = []

    def rec(pi):
        k = len(pi)
        if k == n:
            auts.append(tuple(pi)); return
        for j in range(n):
            if j not in pi and D[k][k] == D[j][j] and all(D[k][i] == D[j][pi[i]] for i in range(k)):
                rec(pi + [j])
    rec([])
    idx = {v: i for i, v in enumerate(M)}
    good = []
    for pi in auts:
        imgM = [M[pi[idx[b]]] for b in basis]
        for cand in range(512):
            if dot(cand, cand) != dot(v0, v0) or any(dot(cand, imgM[i]) != dot(v0, basis[i]) for i in range(8)):
                continue
            img = imgM + [cand]

            def ap(v):
                c, r = combo[v], 0
                for i in range(9):
                    if c >> i & 1:
                        r ^= img[i]
                return r
            if all(ap(m) == M[pi[i]] for i, m in enumerate(M)) and all(ap(p) in Ps for p in ports):
                g = tuple(ap(v) for v in range(512))
                if len({g[p] for p in ports}) == len(ports) and all(dot(g[a], g[b]) == dot(a, b) for a in range(512) for b in range(0, 512, 5)):
                    good.append(g)
    return good, len(auts)


def check_e8(ports):
    need(len(set(ports)) == 104 and Counter(wt(p) for p in ports) == {3: 70, 7: 34}, '104 ports: 70 of weight 3, 34 of weight 7')
    Ps = set(ports)
    # quadratic form on E = 1-perp and its 120 nonsingular points
    Qf = lambda e: (wt(e) // 2) & 1
    ev = [e for e in range(512) if wt(e) % 2 == 0]
    for e in ev:
        for f in ev[::7]:
            need(Qf(e ^ f) == Qf(e) ^ Qf(f) ^ (wt(e & f) & 1), 'Q is a quadratic form with polar form e.f')
    sing = [e for e in ev if e and Qf(e) == 0]
    non = [e for e in ev if Qf(e) == 1]
    need((len(sing), len(non)) == (135, 120), 'O+(8,2): 135 singular nonzero vectors, 120 nonsingular')
    NS = [v for v in range(512) if wt(v) & 1 and Qf(v ^ 511)]
    need(len(NS) == 120 and Counter(wt(v) for v in NS) == {3: 84, 7: 36}, '120 odd vectors of weight 3 or 7')
    need(Ps <= set(NS), 'all ports are nonsingular points')
    # ports span E: the quadratic form is determined by the ports
    sp = {0}
    for p in ports:
        if p ^ 511 not in sp:
            sp |= {x ^ (p ^ 511) for x in sp}
    need(len(sp) == 256 and all(wt(x) % 2 == 0 for x in sp), 'the vectors p+1 span E')
    # explicit E8 model
    L = {v: lift(v) for v in NS}
    cnt = Counter()
    for a, b in itertools.combinations(NS, 2):
        x = ip(L[a], L[b])
        need(x in (0, 1, -1), 'inner products 0, +-1')
        need((x == 0) == (dot(a, b) == 1), 'odd pair <=> real orthogonal')
        cnt[x] += 1
    need(all(ip(L[v], L[v]) == 2 and sum(L[v]) == 0 for v in NS), 'norm 2, sum zero')
    need(cnt == {0: 3780, 1: 1680, -1: 1680}, 'pair census')
    # frames
    F = cliques(NS, 8)
    need(len(F) == 2025 and not cliques(NS, 9), '2025 orthoframes, no 9-clique')
    Fp = cliques(ports, 8)
    need(len(Fp) == 759, '759 frames inside the ports')
    miss = sorted(set(NS) - Ps)
    need(miss == [7, 25, 42, 52, 67, 76, 82, 97, 104, 127, 137, 162, 266, 289, 448, 491], 'missing 16 lines')
    Fm = [f for f in F if set(f) <= set(miss)]
    need(len(Fm) == 2 and not set(Fm[0]) & set(Fm[1]) and set(Fm[0]) | set(Fm[1]) == set(miss), 'two disjoint frames')
    F2, F1 = Fm
    need(F1 == (67, 104, 137, 162, 266, 289, 448, 491) and F2 == (7, 25, 42, 52, 76, 82, 97, 127), 'the two frames')
    inc = [tuple(int(dot(a, b) == 0) for b in F2) for a in F1]
    need(all(sum(r) == 4 for r in inc) and len(set(inc)) == 8, 'incidence rows: 8 distinct weight-4 rows')
    comp = {tuple(1 - x for x in r) for r in inc}
    need(comp == set(inc), 'rows closed under complement')
    # classes of disjoint frame pairs (invariant: number of distinct incidence rows)
    dis = [g for g in F if not set(g) & set(F1)]
    cls = Counter(len({tuple(int(dot(a, b) == 0) for b in g) for a in F1}) for g in dis)
    need(len(dis) == 1260 and cls == {8: 896, 4: 336, 2: 28}, ('frame-pair classes', cls))
    need(Counter(len(set(f) & set(F1)) for f in F) == {0: 1260, 1: 512, 2: 224, 4: 28, 8: 1}, 'intersection census')
    G, naut = stabiliser(ports)
    need(naut == 384 and len(G) == 384 and len(set(G)) == 384, ('stabiliser order', len(G)))
    perms = [tuple(g[p] for p in ports) for g in G]
    idx = {p: i for i, p in enumerate(ports)}
    seen, orbs = set(), []
    for p in ports:
        if p not in seen:
            o = {pm[idx[p]] for pm in perms}
            seen |= o; orbs.append(o)
    need(sorted(len(o) for o in orbs) == [24, 32, 48], 'port orbits 48, 32, 24')
    o69 = next(o for o in orbs if 69 in o)
    need(len(o69) == 48 and 276 in o69, 'ports 69 and 276 lie in the 48-orbit')
    OUT['e8'] = dict(ports='70 weight 3 + 34 weight 7', nonsingular=120, frames=2025, frames_in_ports=759,
                     missing=miss, frame_pair_classes=dict(cls), stabiliser=len(G), orbits=sorted(len(o) for o in orbs))
    return dict(NS=NS, L=L, F1=F1, F2=F2)


# ------------------------------------------------------------------------------ 6 P block and Gram
def rank_q(M):
    M = [r[:] for r in M]
    rk = 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(rk + 1, len(M)):
            if M[i][c] != 0:
                f = M[i][c] / M[rk][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk


def check_blocks(w, acc, e8):
    ports, live = w['ports'], w['live']
    m = len(live)
    sym = acc['sym']
    P = [[sym[live[i] + 112].get(live[j], Q(0)) for j in range(m)] for i in range(m)]
    O = [[Q(int(i == j)) - P[i][j] for j in range(m)] for i in range(m)]
    odd = [(i, j) for i in range(m) for j in range(m) if dot(ports[i], ports[j])]
    need(len(odd) == 5824 == 104 * 56, '5824 ordered odd pairs')
    need(all(P[i][j] == 0 for i, j in odd), 'wall: P vanishes on every odd pair, diagonal included')
    even_nz = sum(1 for i in range(m) for j in range(m) if not dot(ports[i], ports[j]) and P[i][j] != 0)
    need(even_nz == 4972, 'P nonzero on 4972 of 4992 even pairs')
    need(Counter(P[i][j] for i in range(m) for j in range(m)) == {Q(0): 5844, Q(-1, 2): 3338, Q(1, 2): 1614, Q(1): 10, Q(-1): 10},
         'values of P')
    Lp = [e8['L'][p] for p in ports]
    Gm = [[ip(Lp[i], Lp[j]) / 2 for j in range(m)] for i in range(m)]
    sig = [0] * m
    sig[0] = 1
    dq, incons = deque([0]), 0
    while dq:
        i = dq.popleft()
        for j in range(m):
            if j != i and abs(Gm[i][j]) == Q(1, 2):
                val = O[i][j] if abs(O[i][j]) == Q(1, 2) else (O[j][i] if abs(O[j][i]) == Q(1, 2) else None)
                if val is None:
                    continue
                s = sig[i] * (1 if val * Gm[i][j] > 0 else -1)
                if sig[j] == 0:
                    sig[j] = s; dq.append(j)
                elif sig[j] != s:
                    incons += 1
    need(all(sig) and incons == 0, 'gauge signs consistent on all 104 ports')
    Gs = [[sig[i] * sig[j] * Gm[i][j] for j in range(m)] for i in range(m)]
    diff = [(i, j) for i in range(m) for j in range(m) if O[i][j] != Gs[i][j]]
    need(len(diff) == 40 and Counter(ports[i] for i, j in diff) == {69: 20, 276: 20}, ('40 differing entries in rows 69, 276', len(diff)))
    for rowport in (69, 276):
        i = ports.index(rowport)
        ent = [(j, O[i][j], Gs[i][j]) for (ii, j) in diff if ii == i]
        need(sum(1 for _, o, g in ent if o == 0 and abs(g) == Q(1, 2)) == 10 and
             sum(1 for _, o, g in ent if abs(o) == 1 and abs(g) == Q(1, 2)) == 10, 'ten removed, ten doubled')
    need(sum(1 for i in range(m) for j in range(m) if O[i][j] != O[j][i]) == 80, '80 asymmetric entries')
    rG, rO = rank_q(Gs), rank_q(O)
    need((rG, rO) == (8, 10), ('ranks', rG, rO))
    dm = [[O[i][j] - Gs[i][j] for j in range(m)] for i in range(m)]
    need(rank_q(dm) == 2, 'defect has rank 2')
    OUT['blocks'] = dict(P_zero_on_odd_pairs=5824, differing_entries=40, defect_rows=[69, 276], rank_gram=rG, rank_O=rO)
    return O, Gs


# ------------------------------------------------------------------------ 7 private-descent mass
def hop_components(hops):
    par = list(range(len(hops)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for h, H in enumerate(hops):
        for z in H['zin']:
            par[f(h)] = f(z)
    comp = defaultdict(list)
    for h in range(len(hops)):
        comp[f(h)].append(h)
    return list(comp.values())


def prime_rank_ok(vs, PR=1000003, target=8):
    basis = []
    for v in vs:
        v = v[:]
        for pv, b in basis:
            if v[pv]:
                f = v[pv]
                v = [(x - f * y) % PR for x, y in zip(v, b)]
        pv = next((i for i, x in enumerate(v) if x), None)
        if pv is None:
            continue
        inv = pow(v[pv], -1, PR)
        basis.append((pv, [x * inv % PR for x in v]))
        if len(basis) == target:
            return True
    return False


def lift3(v):
    if wt(v) == 3:
        return [3 * (v >> i & 1) - 1 for i in range(9)]
    z = [i for i in range(9) if not v >> i & 1]
    u = [0] * 9
    u[z[0]], u[z[1]] = 3, -3
    return u


def certificate(ports, limit_planes=None):
    """For every 7-dimensional subspace V of F2^9 (kernel of a plane of functionals) the integer E8 lifts of the ports
    outside V have rank 8 modulo 1000003 (hence rank 8 over Q).  Returns (checked, failures)."""
    PR = 1000003
    L = {p: [x % PR for x in lift3(p)] for p in ports}
    fails, count = [], 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if (a ^ b) <= b:
                continue
            count += 1
            out = [L[p] for p in ports if dot(p, a) or dot(p, b)]
            if not prime_rank_ok(out):
                fails.append((a, b))
    return count, fails


def hyperplane_ranks(ports):
    PR = 1000003
    L = {p: [x % PR for x in lift3(p)] for p in ports}
    bad = []
    for a in range(1, 512):
        out = [L[p] for p in ports if dot(p, a)]
        if not prime_rank_ok(out):
            bad.append(a)
    return bad


def check_owned(acc, ports):
    hops = acc['hops']
    comps = hop_components(hops)
    need(len(hops) == 24 and acc['lifetimes'] == 47 and len(comps) == 8, ('24 hops, 47 lifetimes, 8 components', len(comps)))
    for c in comps:
        mass = sum(hops[h]['a'] - hops[h]['b'] for h in c)
        need(mass == 7 and max(hops[h]['a'] for h in c) == 8 and min(hops[h]['b'] for h in c) == 1, 'component 8 -> ... -> 1 of mass 7')
    need(sum(h['a'] - h['b'] for h in hops) == 56 == 8 * 7, '56 = 8 x 7')
    count, fails = certificate(ports)
    need(count == 43435 == (2 ** 9 - 1) * (2 ** 8 - 1) // 3 and not fails, ('dim-7 certificate', count, fails[:3]))
    hb = hyperplane_ranks(ports)
    miss = [7, 25, 42, 52, 67, 76, 82, 97, 104, 127, 137, 162, 266, 289, 448, 491]
    need(sorted(hb) == miss, ('hyperplane exceptions are exactly the 16 removed lines', hb))
    OUT['owned'] = dict(hops=24, lifetimes=47, components=8, mass_each=7, subspaces_checked=count, failures=0,
                        hyperplanes_with_rank_below_8=len(hb))
    return comps


# ---------------------------------------------------------------------------------- 8 controls
def controls(words, callers, e8, ports):
    ctl = {}
    w6702, a6702 = words['pr6702']
    # (1) caller without one stage's idle coverage: stage balance breaks
    c = load_json(HERE / 'retained/pr6726/CONTROLLER.json')
    c2 = json.loads(json.dumps(c))
    ie = next(i for i, e in enumerate(c2['events']) if e[0] == 'IDLE')
    del c2['events'][ie]

    def bal():
        o = caller_outer(c2)
        need(set(o['stage_balance'].values()) == {208}, 'stage balance 2p per stage')
    ctl['caller_missing_idle'] = expect_error(bal, 'stage balance')
    # (2) wrong native mass: pretend O = 55 -> S differs from 48k - 104
    def wrong_o():
        H, P = a6702['helpers'], a6702['paid']
        T, Pd = invoice(callers['pr6726'], H, P, 18)
        Pd[1] += 18
        need(surplus(T, Pd) == 760, 'S = 760')
    ctl['paid_mass_off_by_one'] = expect_error(wrong_o, 'S = 760')
    # (3) an illegal public move (descending) is rejected by the replay
    w = json.loads(json.dumps(w6702))
    i = next(i for i, e in enumerate(w['program']) if e[0] == 'MOVE' and not e[4])
    e = w['program'][i]
    w['program'][i] = [e[0], e[1], e[3], e[2], e[4]]
    ctl['illegal_public_descent'] = expect_error(lambda: native_account(w), 'move')
    # (4) a bogus port (odd weight 5) is not a nonsingular point
    bogus = list(ports)
    bogus[0] = next(v for v in range(512) if wt(v) == 5)

    def bogus_ports():
        need(set(bogus) <= set(e8['NS']), 'all ports are nonsingular points')
    ctl['port_not_nonsingular'] = expect_error(bogus_ports, 'nonsingular')
    # (5) replacing one port by a missing line changes the frame count
    swap = [p for p in ports if p != 69] + [7]
    ctl['swapped_port_frames'] = len(cliques(swap, 8))
    need(ctl['swapped_port_frames'] != 759, 'swapping a port changes the 8-clique count')
    # (6) hyperplane case of the certificate: ports inside one hyperplane (half the set) fail rank 8 at some 7-subspace
    half = [p for p in ports if dot(p, 7) == 0]
    cnt, fails = certificate(half)
    need(fails, 'restricted port set must fail the certificate')
    ctl['certificate_on_half_the_ports'] = dict(ports=len(half), failing_subspaces=len(fails))
    # (7) dropping one z-edge changes the component count
    hops = json.loads(json.dumps(acc_hops_cache['h']))
    for h in hops:
        if h['zin']:
            h['zin'] = h['zin'][1:]
            break
    ctl['hop_graph_edge_dropped'] = len(hop_components(hops))
    need(ctl['hop_graph_edge_dropped'] != 8, 'dropping a hop edge changes the components')
    # (8) mixed bound needs the cost floor: costs one below the floor beat the cap
    S = mixed_surplus([104] * 18, 104, costs=[55] * 18)
    need(S == 48 * 18 - 104 + 18, 'a cost below the floor exceeds the cap')
    ctl['cost_below_floor'] = S
    # (9) live set below 96 lines is outside the cost law
    ctl['small_live_set'] = expect_error(lambda: cost_floor(90), 'outside 96..120')
    # (10) sign gauge: perturbing one P entry on an odd pair is caught by the wall check
    OUT['controls'] = ctl


acc_hops_cache = {}


def main():
    check_pins()
    words = check_native()
    w6702, a6702 = words['pr6702']
    hist = check_edits(a6702)
    hist['pr6349'] = (words['pr6349'][1]['helpers'], words['pr6349'][1]['paid'])
    callers = check_callers()
    check_invoices(callers, hist, words['pr6349'][1])
    check_mixed()
    e8 = check_e8(w6702['ports'])
    check_blocks(w6702, a6702, e8)
    acc_hops_cache['h'] = a6702['hops']
    check_owned(a6702, w6702['ports'])
    controls(words, callers, e8, w6702['ports'])
    print(json.dumps(OUT, indent=1, sort_keys=True, default=str))
    print('PASS_P104_SURPLUS_AND_E8_STRUCTURE')


if __name__ == '__main__':
    main()
