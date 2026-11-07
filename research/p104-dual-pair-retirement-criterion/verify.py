#!/usr/bin/env python3
"""Exact checks for the pure dual-pair retirement criterion.  Python 3.12, standard library only.

Run:  python3 -B research/p104-dual-pair-retirement-criterion/verify.py
Expected marker: PASS_DUAL_PAIR_RETIREMENT_CRITERION

Checks (all exact, Fraction/int; failures raise ValueError, so they stay active under -O):
  0. retained input bytes against SOURCE-PINS.json (SHA-256 and Git blob ids)
  1. unimodular completion over Z[1/2]: Euclid on odd parts, randomised, plus the helper-basis example
  2. small explicit rings: unit-count versus rank (rank-1 pairing with no retirement), zero pairing
  3. literal callers of #6716 and #6726: endpoint is the declared diagonal (hypothesis H1), census of
     every non-ordinary cut for every equal-target class and job s, the retired word replayed
     with a freshly computed completion and compared with the predicted endpoint
  4. literal #6805 native word: the retimed word, class of helper 368 at frame 243, completion, retired
     endpoint on all 771 public inputs; the same cut with the retimed role removed from the frame
  5. negative controls: wrong pivot, non-pure row, non-pure column, zero pairing, frame too small
"""
import gzip
import hashlib
import json
import random
import sys
from collections import defaultdict
from fractions import Fraction as Q
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dualpair import (accumulate, completion, flat, gram_report, need, odd_part, pair_lattices,  # noqa: E402
                      smith_pair, snf, unit_reduce, apply_events_vec, invariants_over_D)
import words as W  # noqa: E402

OUT = {}


# ---------------------------------------------------------------------------------------- 0 pins
def check_pins():
    pins = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    OUT['retained_inputs'] = len(pins)


def expect_error(fn, tag):
    try:
        fn()
    except ValueError as e:
        need(tag in str(e), ('wrong failure', tag, str(e)))
        return str(e)[:80]
    raise ValueError(('control accepted: ' + tag))


# ------------------------------------------------------------------------- 1 completion over Z[1/2]
def check_completion():
    rnd = random.Random(20261106)
    done = 0
    while done < 400:
        n = rnd.randint(2, 6)
        c = {i: Q(rnd.randint(-12, 12), 2 ** rnd.randint(0, 4)) for i in range(n)}
        c = {i: x for i, x in c.items() if x}
        g = 0
        for x in c.values():
            g = gcd(g, odd_part(x.numerator))
        if g != 1:
            continue
        p = rnd.randrange(n)
        ev = unit_reduce(c, p)
        need(apply_events_vec(ev, c) == {p: Q(1)}, 'reduction')
        cols = [apply_events_vec(ev, {j: Q(1)}) for j in range(n)]
        d0 = {j: cols[j].get(p, Q(0)) for j in range(n)}
        # a second, independent row d with d.c = 1: add w with w.c = 0 (w = c_j e_i - c_i e_j)
        d = dict(d0)
        i, j = rnd.sample(range(n), 2)
        k = Q(rnd.randint(-3, 3))
        d[i] = d.get(i, Q(0)) + k * c.get(j, Q(0))
        d[j] = d.get(j, Q(0)) - k * c.get(i, Q(0))
        d = {a: x for a, x in d.items() if x}
        need(sum(d.get(a, 0) * c.get(a, 0) for a in range(n)) == 1, 'dual pair')
        Eev, Einv = completion(c, d, p)
        need(apply_events_vec(Eev, {p: Q(1)}) == c, 'E e_p = c')
        cols = [apply_events_vec(Einv, {j2: Q(1)}) for j2 in range(n)]
        need({j2: cols[j2].get(p, Q(0)) for j2 in range(n) if cols[j2].get(p)} == d, 'e_p^T E^-1 = d')
        for j2 in range(n):
            need(apply_events_vec(Eev, apply_events_vec(Einv, {j2: Q(1)})) == {j2: Q(1)}, 'E E^-1 = I')
        done += 1
    # helper-basis example a=(3,5), b=(2,-1): a.b = 1 although neither has a unit entry
    a, b = {0: Q(3), 1: Q(5)}, {0: Q(2), 1: Q(-1)}
    Eev, Einv = completion(b, a, 0)
    need(apply_events_vec(Eev, {0: Q(1)}) == b, 'example column')
    OUT['completion_trials'] = done


# ------------------------------------------------------------------------------- 2 small rings
def toy_P(N):
    n = len(N)

    def P(i):
        row = {}
        for j in range(n):
            el = {}
            if i == j:
                el[(0,)] = (Q(1), Q(0))
            if N[i][j]:
                el[(1,)] = (Q(N[i][j]), Q(0))
            if el:
                row[j] = el
        return row
    return P


def check_toys():
    one = {(0,): (Q(1), Q(0))}
    # (i) P = I + tN, N nilpotent (so P is invertible over D[t,1/t]; endpoint tau = 1, s = 1, G = R_F = all)
    N = [[0, 3, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]
    P = toy_P(N)
    V, A, ds, Gram = pair_lattices(P, range(4), range(4), range(4), one)
    rep = gram_report(Gram)
    need((len(V), len(A)) == (2, 2) or (len(V), len(A)) == (2, 1) or len(V) and len(A), 'toy lattices')
    need(rep['rank'] == 1 and rep['units'] == 0 and rep['divisors'] == [3], ('toy rank 1 without a unit', rep))
    vals = set()
    for cs in range(-6, 7):
        for cv in range(-6, 7):
            for dk in range(-6, 7):
                for dl in range(-6, 7):
                    c = [cs * x for x in [V[0].get(j, 0) for j in range(4)]]
                    c2 = [cv * V[1].get(j, 0) for j in range(4)] if len(V) > 1 else [0] * 4
                    d = [dk * ds[0].get(j, 0) for j in range(4)]
                    d2 = [dl * ds[1].get(j, 0) for j in range(4)] if len(ds) > 1 else [0] * 4
                    vals.add(sum((x + y) * (z + w) for x, y, z, w in zip(c, c2, d, d2)))
    need(all(v % 3 == 0 for v in vals) and 3 in vals or -3 in vals, 'every pairing value is a multiple of 3')
    expect_error(lambda: completion({1: Q(1), 2: Q(-3)}, {2: Q(1)}, 1), 'dual pair needs d.c = 1')
    OUT['toy_rank_without_unit'] = dict(P='I+tN', N=N, gram=[[str(x) for x in r] for r in Gram], divisors=rep['divisors'],
                                        pairing_values_checked=len(vals))
    # (ii) Jordan block: pure column and pure row exist, pairing zero
    N = [[0, 1, 0], [0, 0, 1], [0, 0, 0]]
    P = toy_P(N)
    V, A, ds, Gram = pair_lattices(P, range(3), range(3), range(3), one)
    need(len(V) == 1 and len(A) == 1 and gram_report(Gram)['rank'] == 0, 'Jordan toy: both pure, pairing zero')
    OUT['toy_zero_pairing'] = dict(V=len(V), A=len(A), gram=[[str(x) for x in r] for r in Gram])


# --------------------------------------------------------------------------------- 3 callers
def row_pairing(rows, n, G, s, RF=None):
    P = lambda i: {j: rows[i][j] for j in range(n) if rows[i][j]}  # noqa: E731
    return P, pair_lattices(P, range(n), G, RF if RF is not None else range(n), s)


def caller_u(rows, n, c, s):
    svec = flat(s)
    k0 = min(svec)
    u = {}
    for i in range(n):
        tot = sum(c[j] * flat(rows[i][j]).get(k0, Q(0)) for j in c if rows[i][j])
        if tot:
            u[i] = tot / svec[k0]
    return u


def caller_retire(w, cut, piv, s, c, d, u, a):
    """Replay: E; prefix; A; rename pivot to a fresh input; A^-1; suffix; E^-1.  Raises on any mismatch."""
    need(sum(d.get(j, 0) * c.get(j, 0) for j in set(d) & set(c)) == 1 and
         sum(a.get(i, 0) * u.get(i, 0) for i in set(a) & set(u)) == 1, 'dual pair needs d.c = 1')
    Eev, Einv = completion(c, d, piv)
    Aab, Aev = completion(u, a, piv)  # A^-1 = E(u,a), A = E(u,a)^-1
    R, n, width, cols = W.init(w, extra=1)
    W.run(R, Eev, width, cols)
    W.run(R, w['events'][:cut + 1], width, cols)
    W.run(R, Aev, width, cols)
    for i in range(n):
        for j in range(n):
            if i == piv or j == piv:
                need(R[i][j] == (s if i == j == piv else {}), 'not decoupled at the pivot')
    R[piv] = [{} for _ in range(cols)]
    R[piv][n] = {(0,) * width: W.ONE}
    W.run(R, Aab, width, cols)
    W.run(R, w['events'][cut + 1:], width, cols)
    W.run(R, Einv, width, cols)
    key = lambda i: tuple(x % 4 if k == 0 else x for k, x in enumerate(w['diagonal'][i]))  # noqa: E731
    for i in range(n):
        for j in range(cols):
            if i == piv and j == n:
                continue
            exp = {key(i): W.ONE} if (i == j and i != piv) else {}
            need(R[i][j] == exp, 'endpoint mismatch')
    need(W.caller_rmul(s, R[piv][n]) == {key(piv): W.ONE}, 'endpoint mismatch: new job is not tau/s')
    return dict(E=len(Eev), A=len(Aev))


def unit_multiple(x, y):
    """True if the dict vectors x and y differ by a unit of Z[1/2] (+-2^k)."""
    ks = [k for k in set(x) | set(y)]
    k0 = next(k for k in ks if x.get(k) and y.get(k))
    r = Q(y[k0]) / Q(x[k0])
    ok = odd_part(r.numerator) == 1 and odd_part(r.denominator) == 1
    return ok and all(Q(y.get(k, 0)) == r * Q(x.get(k, 0)) for k in ks)


def nontrivial(m, kd, tg):
    return not ((m[0] % 4 == 0 and not any(m[1:])) or
                ((m[0] - tg[0]) % (4 if kd == 0 else 2) == 0 and list(m[1:]) == list(tg[1:])))


def census(w):
    """Every non-ordinary cut, every equal-target class, every job s: lattices and Smith divisors."""
    rows, n, width, cols = W.init(w)
    cls = defaultdict(list)
    for r in range(n):
        cls[tuple(w['diagonal'][r])].append(r)
    hits, gaps = [], []
    for k, e in enumerate(w['events']):
        W.step(rows, e, width, cols)
        if e[0] in ('ADD', 'SCALE', 'SWAP'):  # ordinary events leave V, the pairing and its Gram unchanged
            continue
        P = lambda i: {j: rows[i][j] for j in range(n) if rows[i][j]}  # noqa: E731
        for tg, G in cls.items():
            for m, kd in W.candidates(rows, G, n):
                if not nontrivial(m, kd, tg):
                    continue
                V, A, ds, Gram = pair_lattices(P, range(n), G, range(n), W.sdef(m, kd))
                if V and A:
                    rep = gram_report(Gram)
                    if rep['rank']:
                        (hits if rep['units'] else gaps).append((k, tuple(G), m[0], kd, rep['units'], rep['rank']))
    return hits, gaps


def endpoint_check(w):
    rows, n, width, cols = W.init(w)
    W.run(rows, w['events'], width, cols)
    W.endpoint_is_diagonal(w, rows, n)


def check_callers():
    res = {}
    # ---- #6716, unretired caller; published witness at cut 353
    w16 = json.loads((HERE / 'retained/pr6716/CONTROLLER-UNRETIRED.json').read_text())
    wit16 = json.loads((HERE / 'retained/pr6716/WITNESS.json').read_text())
    endpoint_check(w16)
    hits, gaps = census(w16)
    need(hits == [(353, (4, 20, 21), 1, -1, 1, 1)] and not gaps, ('#6716 census', hits, gaps))
    res['pr6716_unretired'] = dict(non_ordinary_cut_hits=hits, rank_without_unit=gaps)
    cut, piv, G = wit16['cut_after'], wit16['pivot'], wit16['group']
    s16 = W.sdef((1,) + (0,) * 19, -1)
    rows, n, width, cols = W.init(w16)
    W.run(rows, w16['events'][:cut + 1], width, cols)
    P, (V, A, ds, Gram) = row_pairing(rows, n, G, s16)
    need((len(V), len(A), gram_report(Gram)['units']) == (1, 1, 1), 'six-teen pair')
    c, d, a = smith_pair(Gram, ds, V, A)
    u = caller_u(rows, n, c, s16)
    # the published dual pair lies in the same one-dimensional lattices: published (a,d) are the unit multiples
    pa = {int(k): Q(v) for k, v in wit16['a'].items()}
    pc = {int(k): Q(v) for k, v in wit16['d'].items()}
    need(unit_multiple(a, pa), 'published a is a unit multiple of the computed generator')
    need(unit_multiple(c, pc), 'published column is a unit multiple of the computed generator')
    res['pr6716_retire'] = caller_retire(w16, cut, piv, s16, c, d, u, a)
    res['pr6716_pair'] = dict(cut=cut, G=G, c={str(k): str(v) for k, v in sorted(c.items())},
                              d={str(k): str(v) for k, v in sorted(d.items())},
                              u={str(k): str(v) for k, v in sorted(u.items())}, a={str(k): str(v) for k, v in sorted(a.items())})
    # ---- controls on #6716
    ctl = {}
    # wrong pivot: role 0 is outside the equal-target class
    ctl['wrong_pivot'] = expect_error(lambda: caller_retire(w16, cut, 0, s16, c, d, u, a), 'endpoint mismatch')
    # non-pure row: a + (u_j e_i - u_i e_j) still pairs to 1 with u but a'P leaves s*D^G
    i, j = sorted(u)[:2]
    a2 = dict(a)
    a2[i] = a2.get(i, 0) + u[j]
    a2[j] = a2.get(j, 0) - u[i]
    a2 = {k: x for k, x in a2.items() if x}
    need(sum(a2.get(k, 0) * u.get(k, 0) for k in u) == 1, 'control keeps a.u = 1')
    ctl['non_pure_row'] = expect_error(lambda: caller_retire(w16, cut, piv, s16, c, d, u, a2), 'not decoupled')
    # non-pure column: c + (d_j e_i - d_i e_j) keeps d.c = 1 but P c' leaves s*D^RF
    i, j = sorted(d)[:2]
    c2 = dict(c)
    c2[i] = c2.get(i, 0) + d[j]
    c2[j] = c2.get(j, 0) - d[i]
    c2 = {k: x for k, x in c2.items() if x}
    need(sum(d.get(k, 0) * c2.get(k, 0) for k in d) == 1, 'control keeps d.c = 1')
    ctl['non_pure_column'] = expect_error(lambda: caller_retire(w16, cut, piv, s16, c2, d, u, a), 'not decoupled')
    # a.u = 0: the job s = 1 has one-dimensional pure lattices on both sides and zero pairing
    one = {(0,) * width: W.ONE}
    _, (V0, A0, ds0, Gram0) = row_pairing(rows, n, G, one)
    need(len(V0) == 1 and len(A0) == 1 and gram_report(Gram0)['rank'] == 0, 'zero pairing at s = 1')
    ctl['a_u_zero_s1'] = dict(V=len(V0), A=len(A0), gram=[[str(x) for x in r] for r in Gram0])
    cz = {int(k): Q(v) for k, v in V0[0].items()}
    az = {int(k): Q(v) for k, v in A0[0].items()}
    uz = caller_u(rows, n, cz, one)
    need(sum(az.get(k, 0) * uz.get(k, 0) for k in uz) == 0, 'a.u = 0')
    ctl['a_u_zero_s1_completion'] = expect_error(
        lambda: caller_retire(w16, cut, piv, one, cz, {k: x for k, x in ds0[0].items()}, uz, az), 'dual pair needs d.c = 1')
    # ---- #6726, unretired caller; census and the two published witnesses
    w26 = json.loads((HERE / 'retained/pr6726/CONTROLLER-UNRETIRED.json').read_text())
    wits26 = json.loads((HERE / 'retained/pr6726/RETIREMENT-WITNESSES.json').read_text())
    endpoint_check(w26)
    hits, gaps = census(w26)
    need(hits == [(158, (6, 7), 0, 0, 1, 1), (383, (4, 5), 1, -1, 1, 1), (392, (4, 5), 1, -1, 1, 1)] and not gaps,
         ('#6726 census', hits, gaps))
    res['pr6726_unretired'] = dict(non_ordinary_cut_hits=hits, rank_without_unit=gaps)
    res['pr6726_retire'] = []
    for k, m0, kd, G26, piv26, cut26 in [(0, None, 0, [6, 7], 6, 158), (1, None, -1, [4, 5], 4, 394),
                                          (2, None, -1, [4, 5], 4, 383)]:
        rows, n, width, cols = W.init(w26)
        W.run(rows, w26['events'][:cut26 + 1], width, cols)
        found = None
        for m, kk in W.candidates(rows, G26, n):
            if kk != kd or not nontrivial(m, kk, w26['diagonal'][G26[0]]):
                continue
            if m0 is not None and m != m0:
                continue
            s26 = W.sdef(m, kk)
            _, (V, A, ds, Gram) = row_pairing(rows, n, G26, s26)
            if V and A and gram_report(Gram)['units']:
                found = (s26, V, A, ds, Gram)
        need(found is not None, ('#6726 pair', cut26))
        s26, V, A, ds, Gram = found
        c, d, a = smith_pair(Gram, ds, V, A)
        u = caller_u(rows, n, c, s26)
        res['pr6726_retire'].append(dict(cut=cut26, G=G26, kind=kd, **caller_retire(w26, cut26, piv26, s26, c, d, u, a)))
    # ---- the #6726 final caller (it is also the caller of #6805): no cut carries a retirement
    w26f = json.loads((HERE / 'retained/pr6726/CONTROLLER.json').read_text())
    endpoint_check(w26f)
    hits, gaps = census(w26f)
    need(not hits and not gaps, ('final caller census', hits, gaps))
    res['pr6726_final_caller'] = dict(non_ordinary_cut_hits=hits, rank_without_unit=gaps, events=len(w26f['events']))
    OUT['callers'] = res
    OUT['caller_controls'] = ctl


# ----------------------------------------------------------------------------------- 4 native
def addrow(dst, src, q):
    for k, v in src.items():
        nv = dst.get(k, 0) + q * v
        if nv:
            dst[k] = nv
        else:
            dst.pop(k, None)


def native_event(rows, e):
    if e[0] == 'ADD':
        addrow(rows[e[1]], rows[e[2]], e[3])
    elif e[0] == 'SCALE':
        rows[e[1]] = {k: v * e[2] for k, v in rows[e[1]].items()}
    else:
        rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]


def native_step(rows, current, e):
    op, r = e[:2]
    if op == 'MOVE':
        current[r] = e[3]
    elif op == 'INIT':
        rows[r] = {}
        current[r] = e[2]
    elif op == 'CLEAR':
        rows[r] = {}
        current[r] = None
    elif op == 'SCALE':
        rows[r] = {k: v * Q(e[2]) for k, v in rows[r].items()}
    elif op == 'COPY':
        rows[r] = {k: v * Q(e[3]) for k, v in rows[e[2]].items()}
    else:
        need(op == 'ADD', 'opcode')
        addrow(rows[r], rows[e[2]], Q(e[3]))


def native_retire(prog, n, N, init_frames, G, RFset, piv, c, d, u, a, cut, expected_end):
    Eev, Einv = completion(c, d, piv)
    Aab, Aev = completion(u, a, piv)
    need(all(e[1] in G and (e[0] == 'SCALE' or e[2] in G) for e in Eev + Einv), 'E uses roles outside the class')
    need(all(e[1] in RFset and (e[0] == 'SCALE' or e[2] in RFset) for e in Aev + Aab), 'A uses roles outside the frame')
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    current = list(init_frames) + [None] * (N - n)
    for e in Eev:
        native_event(rows, e)
    for e in prog[:cut + 1]:
        native_step(rows, current, e)
    for e in Aev:
        native_event(rows, e)
    for i in range(N):
        need((i == piv and rows[i] == {piv: Q(1)}) or (i != piv and piv not in rows[i]), 'not decoupled at the pivot')
    rows[piv] = {-1: Q(1)}
    for e in Aab:
        native_event(rows, e)
    for e in prog[cut + 1:]:
        native_step(rows, current, e)
    for e in Einv:
        native_event(rows, e)
    for r in range(N):
        exp = dict(expected_end[r])
        exp.pop(piv, None)
        if r == piv:
            exp = {-1: Q(1)}
        need(rows[r] == exp, 'endpoint mismatch')
    return dict(E=len(Eev), A=len(Aev))


def check_native():
    src = json.loads(gzip.decompress((HERE / 'retained/pr6702/WORD.json.gz').read_bytes()))
    wit = json.loads((HERE / 'retained/pr6805/WITNESS.json').read_text())
    h = wit['screen_hit']
    cut, F, piv = h['cut'], h['frame'], h['pivot']
    need((cut, F, piv) == (12372, 243, 368), 'frozen cut')
    p80 = h['paths'][0]
    need(src['program'][14088] == ['MOVE', 80, 749, 127, False], 'source event')
    for e in src['program'][12372:14088]:
        need(e[1] != 80 and not (e[0] in ('ADD', 'COPY') and e[2] == 80), 'role 80 is untouched on the interval')
    prep = dict(src)
    prep['program'] = (src['program'][:12372] + [['MOVE', 80, 749, 243, False], ['MOVE', 80, 243, 127, False]] +
                       src['program'][12372:14088] + src['program'][14089:])
    prog = prep['program']
    n = prep['public']
    N = n + prep['owned_fields']
    # plain replay: endpoint and the prefix state
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    current = list(prep['initial']) + [None] * prep['owned_fields']
    pre = None
    for i, e in enumerate(prog):
        native_step(rows, current, e)
        if i == cut:
            pre = ([dict(r) for r in rows], list(current))
    end = [dict(r) for r in rows]
    main = set(prep['live']) | {r + 112 for r in prep['live']}
    for r in range(n):
        if r not in main:
            need(end[r] == {r: Q(1)}, 'helper endpoint is the identity: hypothesis H1 (block diagonal, equal target per class)')
    prow, pcur = pre
    U, Vf = prep['initial'][piv], prep['final'][piv]
    G = [r for r in range(n) if r not in main and (prep['initial'][r], prep['final'][r]) == (U, Vf)]
    RF = [r for r in range(N) if pcur[r] == F]
    need(piv in G and piv in RF and 80 in RF, 'pivot and role 80 resident at frame 243')
    s = {(F,): (Q(1), Q(0))}
    Pf = lambda i: {j: {(pcur[i],): (x, Q(0))} for j, x in prow[i].items()}  # noqa: E731
    regs = [i for i in range(N) if prow[i]]
    V, A, ds, Gram = pair_lattices(Pf, regs, G, RF, s)
    rep = gram_report(Gram)
    need((len(A), rep['rank'], rep['units']) == (1, 1, 1), ('native pair', len(V), len(A), rep))
    c, d, a = smith_pair(Gram, ds, V, A)
    u = {}
    for i in regs:
        tot = sum(c[j] * prow[i].get(j, 0) for j in c)
        if tot:
            u[i] = tot
    # published witness: its (a, d) are unit multiples of the computed lattice generators
    pa = {int(k): Q(v) for k, v in wit['split']['a'].items()}
    need(unit_multiple(a, pa), 'published a is a unit multiple of the computed generator')
    res = native_retire(prog, n, N, prep['initial'], set(G), set(RF), piv, c, d, u, a, cut, end)
    out = dict(frame=F, pivot=piv, cut=cut, class_size=len(G), frame_residents=len(RF), V_dim=len(V), A_dim=len(A),
               gram=[[str(x) for x in r] for r in Gram], divisors=rep['divisors'], public_inputs=n,
               a={str(k): str(v) for k, v in sorted(a.items())}, **res)
    ctl = {}
    # frame too small: remove the retimed role 80 from the frame -> no pure row at all
    RF2 = [r for r in RF if r != 80]
    V2, A2, ds2, Gram2 = pair_lattices(Pf, regs, G, RF2, s)
    need(len(A2) == 0 and len(V2) == len(V), 'no pure row without role 80')
    ctl['frame_without_role80'] = dict(V=len(V2), A=len(A2), rank=0)
    # the same cut on the word without the retiming: role 80 is not at frame 243
    rows0 = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur0 = list(src['initial']) + [None] * src['owned_fields']
    for e in src['program'][:cut + 1]:
        native_step(rows0, cur0, e)
    RF0 = [r for r in range(N) if cur0[r] == F]
    Pf0 = lambda i: {j: {(cur0[i],): (x, Q(0))} for j, x in rows0[i].items()}  # noqa: E731
    V0, A0, ds0, Gram0 = pair_lattices(Pf0, [i for i in range(N) if rows0[i]], G, RF0, s)
    need(len(A0) == 0, 'unretimed word has no pure row at frame 243')
    ctl['unretimed_word'] = dict(frame_residents=len(RF0), A=len(A0))
    # wrong pivot: a main role outside the class
    ctl['wrong_pivot'] = expect_error(
        lambda: native_retire(prog, n, N, prep['initial'], set(G) | {80}, set(RF), 80, c, d, u, a, cut, end), 'endpoint mismatch')
    # non-pure row
    i, j = sorted(u)[:2]
    a2 = dict(a)
    a2[i] = a2.get(i, 0) + u[j]
    a2[j] = a2.get(j, 0) - u[i]
    a2 = {k: x for k, x in a2.items() if x}
    need(i in RF and j in RF and sum(a2.get(k, 0) * u.get(k, 0) for k in u) == 1, 'control keeps a.u = 1 inside the frame')
    ctl['non_pure_row'] = expect_error(
        lambda: native_retire(prog, n, N, prep['initial'], set(G), set(RF), piv, c, d, u, a2, cut, end), 'not decoupled')
    OUT['native'] = out
    OUT['native_controls'] = ctl


def main():
    check_pins()
    check_completion()
    check_toys()
    check_callers()
    check_native()
    print(json.dumps(OUT, indent=1, sort_keys=True, default=str))
    print('PASS_DUAL_PAIR_RETIREMENT_CRITERION')


if __name__ == '__main__':
    main()
