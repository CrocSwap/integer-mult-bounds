#!/usr/bin/env python3
"""Rank-8 rigidity of the E-graph system on every P109 unit (P112 minus three lines) outside PR1419's reach.

Standard library only, exact arithmetic. Independent of PR1212's code: own E8 model, stabiliser orbits on
triples, classes, witnesses, gluing, Lemma 9 propagation, zero-pattern CNF and RUP checker. The 19 DRUP
refutations in PROOFS.json.gz were produced by make_proof.py (python-sat); this file replays them. Run from the
repository root:

    python3 -I -B research/complex-rank8-rigidity-p109/verify.py
"""

import gzip
import hashlib
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
        print(f'FAIL_COMPLEX_RANK8_RIGIDITY_P109: {tag}')
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

# UNITS.json: the 19 orbit representatives (punctured triple and pivot frame, as root vectors) with pinned SHA256 of each
# decompressed proof and of the CNF it refutes. Chosen by make_proof.py: the first triple of each orbit in
# verify.py's order, and the first frame inside the live set (in line order) that passes (I3), (I4), gluing and
# Lemma 9 connectivity. The verifier rechecks every property it relies on; the pins only detect drift.
UNITS_FILE = HERE / 'UNITS.json'
# Every 29th stabiliser generator (8 of 204). Orbits under any subgroup are sound for transport; this subset
# already gives the 24 orbits that all 204 generators give (checked by census.triples against PR1419's census).
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


# ---------------------------------------------------------------- zero-pattern CNF (Lemma 8 analogue)

class CNF:
    def __init__(self):
        self.ids, self.clauses = {}, []

    def var(self, key):
        if key not in self.ids:
            self.ids[key] = len(self.ids) + 1
        return self.ids[key]

    def add(self, c):
        self.clauses.append(list(c))


def build_cnf(live, F):
    """Necessary conditions on the zero pattern of a_i = K[i,F] and b_i = K[F,i] (variable TRUE = entry zero)
    for a rank-8 solution of (E), after pivot reduction K = K[:,F] K[F,:] / 4 (rank K = 8, K[F,F] = 4I):
      two   orthogonal i, j with T_i n T_j = {k, k'}: a_ik b_jk + a_ik' b_jk' = 0, so one product vanishes
            iff the other does (both orders i.j and j.i are separate pairs);
      four  orthogonal i, j with T_i = T_j: sum of four products is 0, so not exactly one is nonzero;
      diag  a_i . b_i = 16: some product is nonzero;
      trans complete class C (4 pairwise orthogonal rows): A_C B_C^T = 16 I, so A_C and B_C are nonsingular
            and their zero patterns admit a transversal (some permutation avoids every zero).
    Returns the CNF and the pattern variables; the refuted formula adds the clause OR(pattern variables)."""
    rel = relative(F, live)
    cnf = CNF()
    rows = sorted(rel)
    za = lambda i, f: cnf.var(('a', i, f))
    zb = lambda i, f: cnf.var(('b', i, f))
    for i in rows:
        for f in rel[i][0]:
            za(i, f)
    for i in rows:
        for f in rel[i][0]:
            zb(i, f)
    for i in rows:
        Ti = rel[i][0]
        for j in rows:
            if j == i or G[i][j] != 0:
                continue
            ov = [f for f in Ti if f in rel[j][0]]
            if len(ov) == 2:
                k, kp = ov
                for (p, q), (r, s) in (((za(i, k), zb(j, k)), (za(i, kp), zb(j, kp))),
                                       ((za(i, kp), zb(j, kp)), (za(i, k), zb(j, k)))):
                    cnf.add([-p, r, s])
                    cnf.add([-q, r, s])
            elif len(ov) == 4:
                prods = []
                for k in ov:
                    pk = cnf.var(('p', i, j, k))  # pk <-> a_ik != 0 and b_jk != 0
                    cnf.add([-pk, -za(i, k)])
                    cnf.add([-pk, -zb(j, k)])
                    cnf.add([pk, za(i, k), zb(j, k)])
                    prods.append(pk)
                for pk in prods:
                    cnf.add([-pk] + [q for q in prods if q != pk])
        ds = []
        for k in Ti:
            dk = cnf.var(('d', i, k))
            cnf.add([-dk, -za(i, k)])
            cnf.add([-dk, -zb(i, k)])
            cnf.add([dk, za(i, k), zb(i, k)])
            ds.append(dk)
        cnf.add(ds)
    for (T, par), lines in sorted(classes_of(rel).items()):
        if len(lines) != 4:
            continue
        for which, zf in (('A', za), ('B', zb)):
            perms = []
            for perm in itertools.permutations(range(4)):
                v = cnf.var(('perm', which, T, par, perm))
                for p, i in enumerate(lines):
                    cnf.add([-v, -zf(i, T[perm[p]])])
                perms.append(v)
            cnf.add(perms)
    zvars = [cnf.ids[('a', i, f)] for i in rows for f in rel[i][0]] + \
            [cnf.ids[('b', i, f)] for i in rows for f in rel[i][0]]
    return cnf, zvars


def cnf_digest(clauses):
    return hashlib.sha256('\n'.join(' '.join(map(str, c)) for c in clauses).encode()).hexdigest()


def rup_check(clauses, nvars, proof_text):
    """Replay a DRUP refutation with two-watched-literal unit propagation. Every lemma must be RUP with
    respect to the original clauses and earlier lemmas; deletions are ignored (sound: the database only
    grows); the empty clause must be derived. Returns (ok, lemmas, reason)."""
    db, watches, units = [], {}, []
    empty = [False]

    def add(c):
        c = list(dict.fromkeys(c))
        if not c:
            empty[0] = True
            return
        if len(c) == 1:
            units.append(c[0])
            return
        idx = len(db)
        db.append(c)
        watches.setdefault(c[0], []).append(idx)
        watches.setdefault(c[1], []).append(idx)

    def conflict(assume):
        val = {}
        trail = []

        def setlit(lit):
            v, s = abs(lit), (1 if lit > 0 else -1)
            if v in val:
                return val[v] == s
            val[v] = s
            trail.append(lit)
            return True

        def value(lit):
            s = val.get(abs(lit))
            return None if s is None else (s == 1) == (lit > 0)

        if empty[0]:
            return True
        for lit in units + assume:
            if not setlit(lit):
                return True
        q = 0
        while q < len(trail):
            fl = -trail[q]
            q += 1
            wl = watches.get(fl, [])
            k = 0
            while k < len(wl):
                c = db[wl[k]]
                if c[0] == fl:
                    c[0], c[1] = c[1], c[0]
                if value(c[0]) is True:
                    k += 1
                    continue
                moved = False
                for m in range(2, len(c)):
                    if value(c[m]) is not False:
                        c[1], c[m] = c[m], c[1]
                        watches.setdefault(c[1], []).append(wl[k])
                        wl[k] = wl[-1]
                        wl.pop()
                        moved = True
                        break
                if moved:
                    continue
                if value(c[0]) is False:
                    return True
                setlit(c[0])
                k += 1
        return False

    for c in clauses:
        add(c)
    n = 0
    for line in proof_text.splitlines():
        line = line.strip()
        if not line or line.startswith('c') or line.startswith('d'):
            continue
        lits = [int(t) for t in line.split()]
        if not lits or lits[-1] != 0 or 0 in lits[:-1] or any(abs(x) > nvars for x in lits):
            return False, n, f'malformed lemma {line[:40]}'
        lem = lits[:-1]
        if not conflict([-x for x in lem]):
            return False, n, f'lemma {n} not RUP'
        n += 1
        add(lem)
        if not lem:
            return True, n, 'empty clause derived'
    return False, n, 'no empty clause'


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


def gauge_pattern_satisfies(cnf):
    """Control: the all-nonzero pattern of a gauge solution (every pattern variable FALSE, every product,
    diagonal and permutation variable TRUE) satisfies the CNF without the final 'some zero' clause."""
    truth = {}
    for key, v in cnf.ids.items():
        truth[v] = key[0] in ('p', 'd', 'perm')
    return all(any((truth[abs(x)] if x > 0 else not truth[abs(x)]) for x in c) for c in cnf.clauses)


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


def main():
    check('model.lines', NL == 120 and len(FRAME0) == 8 and is_frame(sorted(FRAME0)), '120 lines; FRAME0 is a frame')
    allgens = stabiliser(FRAME0)
    gens = allgens[::GEN_STEP]
    check('model.generators', len(allgens) == 204 and all(frozenset(g[i] for i in FRAME0) == FRAME0 for g in gens),
          f'{len(gens)} of the {len(allgens)} reflection / reflection-pair generators fixing FRAME0')
    frames = frames_inside(P112)
    inframe = {X for F in frames for X in itertools.combinations(F, 3)}
    orbs = triple_orbits(gens)
    split = [all((X in inframe) == (o[0] in inframe) for X in o) for o in orbs]
    covered = [o for o in orbs if o[0] in inframe]
    open_ = [o for o in orbs if o[0] not in inframe]
    check('census.triples', len(frames) == 1260 and sum(map(len, orbs)) == 227920 and len(orbs) == 24 and all(split)
          and sum(map(len, covered)) == 29232 and len(open_) == 19 and sum(map(len, open_)) == 198688,
          f'227920 triples of P112 in {len(orbs)} orbits; inside-a-frame is constant on orbits; '
          f'{len(covered)} orbits (29232 triples) inside a P112 frame (PR1419), {len(open_)} orbits (198688) not')
    nodd = sorted(odd_pairs(o[0]) for o in open_)
    check('census.open-orbits', [len(o) for o in open_ if odd_pairs(o[0]) == 0] == [1792],
          f'open orbit sizes {[len(o) for o in open_]}; odd pairs per triple {dict((k, nodd.count(k)) for k in sorted(set(nodd)))}; '
          'the only pairwise-orthogonal open orbit has 1792 triples')
    UNITS = json.loads(UNITS_FILE.read_text())
    blob = json.loads(gzip.decompress((HERE / 'PROOFS.json.gz').read_bytes()))
    check('units.cover', sorted(UNITS) == sorted(blob) and len(UNITS) == 19 and
          sorted(next(n for n, o in enumerate(open_) if tuple(sorted(lid(v) for v in u['triple'])) in o)
                 for u in UNITS.values()) == list(range(19)),
          '19 units, one representative in each open orbit; one proof per unit')
    bogus_done = False
    for name, u in sorted(UNITS.items()):
        X = sorted(lid(v) for v in u['triple'])
        F = [lid(v) for v in u['pivot']]
        live = [i for i in P112 if i not in X]
        orb = next(o for o in open_ if tuple(X) in o)
        ok = is_frame(F) and set(F) <= set(live) and len(live) == 109 and d4_structure(F)
        r = inputs(live, F)
        nc = sum(1 for n in r['profile'] if n == 4)
        ok &= r['witnesses'] and r['nwit'] == 12 * nc and r['blocks'] and r['glue'] and r['prop']
        ok9, asm = algebra(live, F, r, 1090 + int(name[1:]))
        cnf, zvars = build_cnf(live, F)
        clauses = cnf.clauses + [zvars]
        text = blob[name]
        digest = hashlib.sha256(text.encode()).hexdigest()
        good, n, why = rup_check(clauses, len(cnf.ids), text)
        nozero, _, _ = rup_check(cnf.clauses, len(cnf.ids), text)
        check(f'{name}.rigid', ok and ok9 and asm and gauge_pattern_satisfies(cnf) and good and not nozero
              and digest == u['proof_sha256'] and cnf_digest(clauses) == u['cnf_sha256'],
              f'orbit {len(orb)}, {odd_pairs(X)} odd pairs; pivot passes D4/(I3)/(I4)/gluing with {nc} complete classes '
              f'and Lemma 9 on {len(r["rest"])} lines; assembly on 109 lines; zero exclusion {n} lemmas ({why}); '
              f'proof fails without the zero clause')
        if not bogus_done:
            bogus, _, why2 = rup_check(clauses, len(cnf.ids), '0\n')
            check('control.bogus-proof', not bogus and 'not RUP' in why2,
                  'an empty-clause-only proof is rejected: unit propagation alone does not refute the CNF')
            bogus_done = True
    print(f'PASS_COMPLEX_RANK8_RIGIDITY_P109: checks {len(RESULTS)}; all 19 open P109 orbits (198688 triples) rigid; '
          f'with PR1419 every P109 unit is rigid; floor 61')


if __name__ == '__main__':
    main()
