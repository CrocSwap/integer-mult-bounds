#!/usr/bin/env python3
"""Every P107 unit (P112 minus five lines) outside a P112 frame has a pivot frame passing every per-unit input
of the PR1212 / PR1399 rigidity method except (I2) zero exclusion: (I3) with live witnesses, (I4) (all 14
blocks complete), gluing, and Lemma 9 connectivity with its sign identity and exact rank-3 algebra.

Standard library only, exact arithmetic. Self-contained: own E8 model, stabiliser orbits on triples, a two-level
candidate coverage argument for 5-subsets with explicit generator words (COVER.json), and per-unit pivot checks
(UNITS.json). Both files were produced by make_units.py (numpy); this file rechecks everything it relies on.
Run from the repository root:

    python3 -I -B research/complex-rank8-p107-pivots/verify.py
"""

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = []


def check(tag, cond, info=''):
    RESULTS.append(tag)
    print(f"{'PASS' if cond else 'FAIL'} {tag}" + (f': {info}' if info else ''))
    if not cond:
        print(f'FAIL_COMPLEX_RANK8_P107_PIVOTS: {tag}')
        sys.exit(1)


# ---------------------------------------------------------------- E8 model (doubled coordinates, norm 8)

def lines_e8():
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for sj in (2, -2):
            v = [0] * 8
            v[i], v[j] = 2, sj
            out.add(tuple(v))
    for s in itertools.product((1, -1), repeat=7):
        v = (1,) + s
        if v.count(-1) % 2 == 0:
            out.add(v)
    return sorted(out)


LINES = lines_e8()
NL = len(LINES)
IDX = {v: n for n, v in enumerate(LINES)}


def canon(v):
    v = tuple(v)
    first = next(a for a in v if a)
    return v if first > 0 else tuple(-a for a in v)


def ip(x, y):
    d = sum(a * b for a, b in zip(x, y))
    assert d % 4 == 0
    return d // 4


G = [[ip(LINES[i], LINES[j]) for j in range(NL)] for i in range(NL)]


def lid(v):
    return IDX[canon(v)]


FRAME0 = frozenset(lid(v) for v in [
    (2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0),
    (0, 0, 0, 0, 2, 2, 0, 0), (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 0, 2, 2), (0, 0, 0, 0, 0, 0, 2, -2)])
P112 = [i for i in range(NL) if i not in FRAME0]

# UNITS.json: one representative 5-subset per open orbit and its pivot frame, as root vectors. COVER.json:
# 180 quadruple representatives; for every quadruple candidate (triple-orbit representative + one line) a
# representative and a word carrying it onto the candidate; and for every 5-subset candidate (quadruple
# representative + one line) not inside a P112 frame, a unit and a word carrying the unit onto it.
UNITS_FILE = HERE / 'UNITS.json'
COVER_FILE = HERE / 'COVER.json'
# Every 29th stabiliser generator (8 of 204), as in the P108 package. Orbits under any subgroup are sound for
# transport.
GEN_STEP = 29


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


def reflection_perm(r):
    rv = LINES[r]
    return tuple(lid(tuple(a - G[i][r] * b for a, b in zip(LINES[i], rv))) for i in range(NL))


def stabiliser(frame):
    refl = [reflection_perm(r) for r in range(NL)]
    gens = [p for p in refl if frozenset(p[i] for i in frame) == frame]
    for p, q in itertools.combinations(refl, 2):
        pq = tuple(p[q[i]] for i in range(NL))
        if frozenset(pq[i] for i in frame) == frame:
            gens.append(pq)
    return gens


# ---------------------------------------------------------------- structure relative to a pivot

def relative(F, lines):
    """line -> (T, eps): T the pivot lines (in pivot order) the line is odd to, eps the signs G_if."""
    out = {}
    for i in lines:
        if i in F:
            continue
        T = tuple(f for f in F if G[i][f] != 0)
        out[i] = (T, tuple(G[i][f] for f in T))
    return out


def parity(eps):
    return sum(1 for s in eps if s < 0) % 2


def classes_of(rel):
    cl = {}
    for i, (T, eps) in rel.items():
        cl.setdefault((T, parity(eps)), []).append(i)
    return cl


def connected(n, edges):
    seen, todo = {0}, [0]
    while todo:
        x = todo.pop()
        for p, q in edges:
            for y in ((q,) if p == x else (p,) if q == x else ()):
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
    return len(seen) == n


def inputs(live, F):
    """PR1212's (I3), (I4) and gluing on the complete classes, and PR1399's Lemma 9 connectivity for the
    remaining lines. Returns a dict of results (all booleans True means the unit passes)."""
    rel = relative(F, live)
    cl = classes_of(rel)
    complete = {k: v for k, v in cl.items() if len(v) == 4}
    known = {i for v in complete.values() for i in v}
    rest = [i for i in rel if i not in known]
    nwit, wit_ok = 0, True
    for (T, _), rows in complete.items():
        for c, c2 in itertools.combinations(range(4), 2):
            for i, i2 in itertools.combinations(rows, 2):
                if rel[i][1][c] * rel[i][1][c2] != rel[i2][1][c] * rel[i2][1][c2]:
                    continue
                nwit += 1
                wit_ok &= any(set(Tj) & set(T) == {T[c], T[c2]} and G[j][i] == 0 and G[j][i2] == 0
                              for j, (Tj, _) in rel.items())
    npair, glue_ok = 0, True
    for c1, c2 in itertools.permutations(complete, 2):
        if c1[0] == c2[0] or len(set(c1[0]) & set(c2[0])) != 2:
            continue
        npair += 1
        glue_ok &= all(sum(1 for i in complete[c1] if G[i][j] == 0) == 2 for j in complete[c2])
    prop_ok, sign_ok, pairs, nw = True, True, [], 0
    for i in rest:
        T, ei = rel[i]
        edges = []
        for c, c2 in itertools.combinations(range(4), 2):
            ws = [j for j in known if G[i][j] == 0 and set(rel[j][0]) & set(T) == {T[c], T[c2]}]
            for j in ws:
                Tj, ej = rel[j]
                sign_ok &= ei[c] * ej[Tj.index(T[c])] == -ei[c2] * ej[Tj.index(T[c2])]
            if ws:
                edges.append((c, c2))
            nw += len(ws)
        pairs.append(len(edges))
        prop_ok &= connected(4, edges)
    profile = sorted(len(v) for v in cl.values())
    return {'rel': rel, 'complete': complete, 'known': known, 'rest': rest, 'profile': profile,
            'blocks': len({T for T, _ in complete}) == 14, 'witnesses': wit_ok, 'nwit': nwit,
            'glue': glue_ok, 'npair': npair, 'prop': prop_ok and sign_ok, 'pairs': pairs, 'nw': nw}


def d4_structure(F):
    """PR1212 Lemma 2 facts relative to F, over all 112 non-pivot lines: each is odd to 4 pivot lines; the 14
    blocks form an S(3,4,8); the 28 classes are 4 pairwise orthogonal lines with orthogonal sign vectors;
    2 G_ij is the sum of sign products over T_i n T_j."""
    rel = relative(F, range(NL))
    blocks = sorted({T for T, _ in rel.values()})
    ok = all(len(T) == 4 and all(abs(x) == 1 for x in e) for T, e in rel.values())
    ok &= len(blocks) == 14 and all(sum(1 for B in blocks if set(t) <= set(B)) == 1
                                    for t in itertools.combinations(F, 3))
    cl = classes_of(rel)
    ok &= len(cl) == 28 and all(
        len(v) == 4 and all(G[i][j] == 0 for i in v for j in v if i != j)
        and all(sum(x * y for x, y in zip(rel[i][1], rel[j][1])) == (4 if i == j else 0) for i in v for j in v)
        for v in cl.values())
    for i, j in itertools.combinations(rel, 2):
        (Ti, ei), (Tj, ej) = rel[i], rel[j]
        ok &= 2 * G[i][j] == sum(ei[Ti.index(f)] * ej[Tj.index(f)] for f in set(Ti) & set(Tj))
    return ok


def passes(r):
    return r['blocks'] and r['witnesses'] and r['glue'] and r['prop']


# ---------------------------------------------------------------- exact algebra for Lemma 9 and assembly

def rank_q(rows):
    M = [[Fraction(x) for x in r] for r in rows]
    rk = 0
    for c in range(len(M[0]) if M else 0):
        p = next((r for r in range(rk, len(M)) if M[r][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(len(M)):
            if r != rk and M[r][c] != 0:
                f = M[r][c] / M[rk][c]
                M[r] = [a - f * b for a, b in zip(M[r], M[rk])]
        rk += 1
    return rk


def lcg(seed):
    x = seed
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) % (1 << 64)
        yield x >> 33


def rand_nonzero(rng):
    while True:
        n, d = next(rng) % 17 - 8, next(rng) % 7 + 1
        if n:
            return Fraction(n, d)


def algebra(live, F, r, seed):
    """Lemma 9 rank-3 cross-check and the PR1212 section 7 assembly on this unit, for random rational g, d'."""
    rel, known, rest = r['rel'], r['known'], r['rest']
    rng = lcg(seed)
    g = {f: rand_nonzero(rng) for f in F}
    dd = {i: rand_nonzero(rng) for i in rel}
    ok = True
    for i in rest:
        T, ei = rel[i]
        wit = [j for j in known if G[i][j] == 0 and len(set(rel[j][0]) & set(T)) == 2]
        rows_a = [[4 / (dd[j] * g[f]) * G[j][f] for f in T] for j in wit]
        rows_b = [[dd[j] * G[j][f] * g[f] for f in T] for j in wit]
        va = [ei[n] * g[f] for n, f in enumerate(T)]
        vb = [ei[n] / g[f] for n, f in enumerate(T)]
        ok &= rank_q(rows_a) == 3 and all(sum(x * y for x, y in zip(row, va)) == 0 for row in rows_a)
        ok &= rank_q(rows_b) == 3 and all(sum(x * y for x, y in zip(row, vb)) == 0 for row in rows_b)
    a = {i: {f: (dd[i] * G[i][f] * g[f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    b = {i: {f: (4 / (dd[i] * g[f]) * G[i][f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    for f in F:
        a[f] = {h: Fraction(4 if h == f else 0) for h in F}
        b[f] = {h: Fraction(4 if h == f else 0) for h in F}
    D = {i: dd[i] / 2 for i in rel}
    D.update({f: 1 / g[f] for f in F})
    asm = all(sum(a[i][f] * b[j][f] for f in F) / 4 == 2 * G[i][j] * D[i] / D[j] for i in live for j in live)
    eqs = all(sum(a[i][f] * b[j][f] for f in F) == (16 if i == j else 0)
              for i in live for j in live if i == j or G[i][j] == 0)
    return ok, asm and eqs


# ---------------------------------------------------------------- main

def frames_inside(live):
    live = sorted(live)
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(cur)
            return
        for n, j in enumerate(cand):
            grow(cur + [j], [k for k in cand[n + 1:] if G[j][k] == 0])

    grow([], live)
    return out


def triple_orbits(gens):
    """Union-find orbits of the gens on 3-subsets of P112 (as sorted line-id triples)."""
    subs = list(itertools.combinations(P112, 3))
    idx = {s: n for n, s in enumerate(subs)}
    par = list(range(len(subs)))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a

    for g in gens:
        for n, s in enumerate(subs):
            a, b = find(n), find(idx[tuple(sorted(g[x] for x in s))])
            if a != b:
                par[a] = b
    orbs = {}
    for n, s in enumerate(subs):
        orbs.setdefault(find(n), []).append(s)
    return sorted(orbs.values(), key=lambda o: (len(o), o[0]))


def odd_pairs(X):
    return sum(1 for a, b in itertools.combinations(X, 2) if G[a][b] != 0)


def apply_word(gens, word, Y):
    for w in word:
        Y = tuple(sorted(gens[w][y] for y in Y))
    return Y


def main():
    check('model.lines', NL == 120 and len(FRAME0) == 8 and is_frame(sorted(FRAME0)), '120 lines; FRAME0 is a frame')
    allgens = stabiliser(FRAME0)
    gens = allgens[::GEN_STEP]
    check('model.generators', len(allgens) == 204 and all(frozenset(g[i] for i in FRAME0) == FRAME0 for g in gens),
          f'{len(gens)} of the {len(allgens)} reflection / reflection-pair generators fixing FRAME0')
    frames = frames_inside(P112)
    inframe = {Y for F in frames for Y in itertools.combinations(F, 5)}
    torbs = triple_orbits(gens)
    check('census.triples', len(frames) == 1260 and len(torbs) == 24 and sum(map(len, torbs)) == 227920,
          '1260 frames inside P112; the generators split the 227920 triples of P112 into 24 orbits')
    cover = json.loads(COVER_FILE.read_text())
    reps4 = [tuple(sorted(lid(v) for v in r)) for r in cover['reps4']]
    # Level 1. Every quadruple Y contains a triple s = h(t) with t a triple-orbit representative, so h^-1(Y) is
    # a candidate t + {x}; each candidate is a word applied to a quadruple representative.
    c4 = sorted({tuple(sorted(o[0] + (x,))) for o in torbs for x in P112 if x not in o[0]})
    ok = len(cover['cover4']) == len(c4) and all(len(set(r)) == 4 and set(r) <= set(P112) for r in reps4)
    for c in c4:
        j, word = cover['cover4'][' '.join(map(str, c))]
        ok &= apply_word(gens, word, reps4[j]) == c
    check('census.cover4', ok, f'{len(c4)} quadruple candidates, each a generator word applied to one of '
          f'{len(reps4)} quadruple representatives: every quadruple of P112 is equivalent to one of them')
    # Level 2. Every 5-subset Z contains a quadruple Y = h(r) with r a representative, so h^-1(Z) = r + {x}.
    # Inside-a-P112-frame is invariant (the group fixes FRAME0); the frame-contained candidates are PR1419's.
    c5 = sorted({tuple(sorted(r + (x,))) for r in reps4 for x in P112 if x not in r})
    open5 = [c for c in c5 if c not in inframe]
    UNITS = json.loads(UNITS_FILE.read_text())
    units = {name: tuple(sorted(lid(v) for v in u['quintuple'])) for name, u in UNITS.items()}
    hit = set()
    ok = len(cover['cover5']) == len(open5)
    for c in open5:
        name, word = cover['cover5'][' '.join(map(str, c))]
        ok &= apply_word(gens, word, units[name]) == c
        hit.add(name)
    check('census.cover5', ok and hit == set(UNITS) and all(u not in inframe and len(set(u)) == 5
                                                           for u in units.values()),
          f'{len(c5)} 5-subset candidates (quadruple representative + one line); {len(c5) - len(open5)} inside a '
          f'P112 frame (PR1419); each of the other {len(open5)} is a generator word applied to one of the '
          f'{len(UNITS)} units, max word length {max(len(w) for _, w in cover["cover5"].values())}')
    # Control: the pivot rule is not vacuous. On the first unit, the first frame inside the live set fails.
    name0 = min(UNITS)
    live0 = [i for i in P112 if i not in units[name0]]
    r0 = inputs(live0, frames_inside(live0)[0])
    check('control.first-frame-fails', not passes(r0),
          f'{name0}: the first frame inside the live set fails ' +
          ', '.join(k for k in ('blocks', 'witnesses', 'glue', 'prop') if not r0[k]))
    d4 = {}
    nfail, stats = [], {'nc': set(), 'rest': set()}
    for name, u in sorted(UNITS.items()):
        X = units[name]
        F = [lid(v) for v in u['pivot']]
        live = [i for i in P112 if i not in X]
        key = frozenset(F)
        if key not in d4:
            d4[key] = is_frame(F) and d4_structure(F)
        ok = d4[key] and set(F) <= set(live) and len(live) == 107
        r = inputs(live, F)
        nc = sum(1 for n in r['profile'] if n == 4)
        ok &= r['witnesses'] and r['nwit'] == 12 * nc and r['blocks'] and r['glue'] and r['prop']
        ok9, asm = algebra(live, F, r, 1070 + int(name[1:]))
        if not (ok and ok9 and asm):
            nfail.append(name)
        stats['nc'].add(nc)
        stats['rest'].add(len(r['rest']))
    check('units.inputs', not nfail,
          f'{len(UNITS)} units: pivot D4 structure, (I3) with live witnesses, (I4) on all 14 blocks, gluing, Lemma 9 '
          f'connectivity, sign identity and rank-3 algebra, and the section 7 assembly identity; '
          f'{min(stats["nc"])}-{max(stats["nc"])} complete classes, Lemma 9 on {min(stats["rest"])}-'
          f'{max(stats["rest"])} lines; {len(d4)} distinct pivots' + (f'; failing {nfail[:5]}' if nfail else ''))
    print(f'PASS_COMPLEX_RANK8_P107_PIVOTS: checks {len(RESULTS)}; every P107 unit outside a P112 frame '
          f'({len(UNITS)} units) has a pivot passing (I3), (I4), gluing and Lemma 9; (I2) zero exclusion is the '
          f'only per-unit input left')


if __name__ == '__main__':
    main()
