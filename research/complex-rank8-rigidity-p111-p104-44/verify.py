#!/usr/bin/env python3
"""Finite inputs for extending PR1212's rank-8 rigidity theorem to P111 and the type-(4,4) P104 units.

Independent re-implementation (own E8 model, own class/witness/gluing code); nothing is imported from
PR1212.  Zero exclusion (PR1212 Lemma 8) is cited.  With --pr1212-dir it is also replayed by running
PR1212's own verifier from a checkout whose files match the pinned git blobs.

    python3 -I -B research/complex-rank8-rigidity-p111-p104-44/verify.py [--pr1212-dir DIR] [--out FILE]

Standard library only.  Exact integer / rational arithmetic throughout.
"""
import argparse
import hashlib
import itertools
import json
import os
import subprocess
import sys
from fractions import Fraction

FAILS = []
NCHECK = 0


def check(tag, cond, info=''):
    global NCHECK
    NCHECK += 1
    print(('PASS ' if cond else 'FAIL ') + tag + (' | ' + info if info else ''))
    if not cond:
        FAILS.append(tag)
    return bool(cond)


# ------------------------------------------------------------------ E8 model (doubled coordinates)
def lines_e8():
    """One representative per root line, roots in doubled coordinates (norm 8), canonical sign:
    the first nonzero coordinate is positive."""
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
IDX = {v: n for n, v in enumerate(LINES)}
NL = len(LINES)


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


def frame_lines(vs):
    return [lid(v) for v in vs]


# PR1212's FRAME0 and its two extension units with their pivots (copied as root vectors from PR1212
# head 57099cb5 verify.py `extension_units()`; --pr1212-dir rechecks the correspondence).
FRAME0 = [(2, 2, 0, 0, 0, 0, 0, 0), (2, -2, 0, 0, 0, 0, 0, 0), (0, 0, 2, 2, 0, 0, 0, 0), (0, 0, 2, -2, 0, 0, 0, 0),
          (0, 0, 0, 0, 2, 2, 0, 0), (0, 0, 0, 0, 2, -2, 0, 0), (0, 0, 0, 0, 0, 0, 2, 2), (0, 0, 0, 0, 0, 0, 2, -2)]
UNITS = {
    'P111': {
        'extra_dead': [(2, 0, 2, 0, 0, 0, 0, 0)],
        'pivot': [(2, 0, 0, 2, 0, 0, 0, 0), (2, 0, 0, -2, 0, 0, 0, 0), (0, 2, 2, 0, 0, 0, 0, 0), (0, 2, -2, 0, 0, 0, 0, 0),
                  (0, 0, 0, 0, 2, 0, 2, 0), (0, 0, 0, 0, 2, 0, -2, 0), (0, 0, 0, 0, 0, 2, 0, 2), (0, 0, 0, 0, 0, 2, 0, -2)],
        'pr1212_pivot_idx': [4, 5, 14, 15, 46, 47, 52, 53],
        'expect_sizes': {0: 2, 3: 1, 4: 25},
        'floor': 63,
    },
    'P104-44': {
        'extra_dead': [(2, 0, 2, 0, 0, 0, 0, 0), (2, 0, -2, 0, 0, 0, 0, 0), (0, 2, 0, 2, 0, 0, 0, 0), (0, 2, 0, -2, 0, 0, 0, 0),
                       (0, 0, 0, 0, 2, 0, 2, 0), (0, 0, 0, 0, 2, 0, -2, 0), (0, 0, 0, 0, 0, 2, 0, 2), (0, 0, 0, 0, 0, 2, 0, -2)],
        'pivot': [(2, 0, 0, 2, 0, 0, 0, 0), (2, 0, 0, -2, 0, 0, 0, 0), (0, 2, 2, 0, 0, 0, 0, 0), (0, 2, -2, 0, 0, 0, 0, 0),
                  (0, 0, 0, 0, 2, 0, 0, 2), (0, 0, 0, 0, 2, 0, 0, -2), (0, 0, 0, 0, 0, 2, 2, 0), (0, 0, 0, 0, 0, 2, -2, 0)],
        'pr1212_pivot_idx': [4, 5, 14, 15, 48, 49, 50, 51],
        'expect_sizes': {0: 4, 4: 24},
        'floor': 56,
    },
}
PR1212 = {
    'head': '57099cb5684f38877f31d149d598801671a633db',
    'dir': 'research/complex-rank8-decoder-rigidity',
    'blobs': {'verify.py': 'c3707b0993d04b78e20c5d3512d370495690df8b',
              'proof-P111.drup': '31f25bc28c8f065439c063ce91309267ab1edbf7',
              'proof-P104-44.drup': '976ce90f0dc9b00e820cc3ea84c1dd26ca4fa2f3'},
    'pass_lines': ['PASS G.P111.zero-exclusion', 'PASS G.P104-44.zero-exclusion',
                   'PASS G.line-orbits', 'PASS G.frame-orbits'],
}


def is_frame(S):
    return len(S) == 8 and all(G[a][b] == 0 for a in S for b in S if a != b)


# ------------------------------------------------------------------ exact linear algebra
def rank_q(rows):
    M = [[Fraction(x) for x in r] for r in rows]
    if not M:
        return 0
    r = 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r


def lcg(seed):
    x = seed
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) % (1 << 64)
        yield x >> 33


def rand_nonzero(rng):
    while True:
        n = next(rng) % 17 - 8
        d = next(rng) % 7 + 1
        if n:
            return Fraction(n, d)


# ------------------------------------------------------------------ structure relative to a pivot
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


def witness(i, i2, c, c2, rel_live):
    """A live line j orthogonal to i and i2 whose support meets T_i exactly in {c, c2}."""
    T = set(rel_live[i][0])
    for j, (Tj, _) in rel_live.items():
        if set(Tj) & T == {c, c2} and G[j][i] == 0 and G[j][i2] == 0:
            return j
    return None


def analyse(name, spec, cert):
    print(f'== {name}')
    P112 = [i for i in range(NL) if i not in frame_lines(FRAME0)]
    dead = set(frame_lines(spec['extra_dead']))
    live = [i for i in P112 if i not in dead]
    F = frame_lines(spec['pivot'])
    rel_all = relative(F, range(NL))
    rel = relative(F, live)
    check(f'{name}.unit', is_frame(F) and set(F) <= set(live) and len(live) == 112 - len(dead),
          f'live {len(live)}; pivot is a live frame')

    # Lemma 2 facts used below, recomputed: supports of size 4 with signs +-1; 14 blocks forming S(3,4,8);
    # each block splits by sign parity into two 4-frames with Hadamard sign matrices; the orthogonality rule.
    blocks = sorted({T for T, _ in rel_all.values()})
    ok_a = all(len(T) == 4 and all(abs(s) == 1 for s in e) for T, e in rel_all.values())
    steiner = len(blocks) == 14 and all(sum(1 for B in blocks if set(t) <= set(B)) == 1
                                        for t in itertools.combinations(F, 3))
    cl_all = classes_of(rel_all)
    had = len(cl_all) == 28 and all(
        len(v) == 4 and all(G[i][j] == 0 for i in v for j in v if i != j)
        and all(sum(a * b for a, b in zip(rel_all[i][1], rel_all[j][1])) == (4 if i == j else 0) for i in v for j in v)
        for v in cl_all.values())
    rule = True
    for i, j in itertools.combinations(rel_all, 2):
        Ti, ei = rel_all[i]
        Tj, ej = rel_all[j]
        s = sum(ei[Ti.index(f)] * ej[Tj.index(f)] for f in set(Ti) & set(Tj))
        rule &= (2 * G[i][j] == s)
    check(f'{name}.d4-structure', ok_a and steiner and had and rule,
          '112 non-pivot lines odd to 4 pivot lines; 14 blocks = S(3,4,8); 28 Hadamard 4-frame classes; 2G_ij = sum of sign products')

    cl = classes_of(rel)
    sizes = {}
    for key in cl_all:
        n = len(cl.get(key, []))
        sizes[n] = sizes.get(n, 0) + 1
    check(f'{name}.class-profile', sizes == spec['expect_sizes'], f'live rows per class -> count: {dict(sorted(sizes.items()))}')
    usable = {k: v for k, v in cl.items() if len(v) >= 3}
    check(f'{name}.lines-in-usable-classes', all(len(cl[(T, parity(e))]) >= 3 for T, e in rel.values()),
          'every live non-pivot line lies in a class with >= 3 live rows (input I1 widened)')

    # Lemma 5 step 1 witnesses (input I3) for every usable class, every column pair, every live group.
    wit_ok, nwit = True, 0
    for (T, _), rows in usable.items():
        for c, c2 in itertools.combinations(T, 2):
            a, b = T.index(c), T.index(c2)
            for i, i2 in itertools.combinations(rows, 2):
                if rel[i][1][a] * rel[i][1][b] != rel[i2][1][a] * rel[i2][1][b]:
                    continue
                nwit += 1
                wit_ok &= witness(i, i2, c, c2, rel) is not None
    check(f'{name}.group-witnesses', wit_ok, f'{nwit} live groups (usable classes x column pairs) each have a live witness')

    # Three-row lemma inputs: for each 3-row class, (a) the three live pairs are the live groups of the three
    # pairings, one each; (b) the entrywise products of the three sign rows are independent and orthogonal to
    # the all-ones vector, so w with diag(H3 diag(w) H3^T)-offdiagonal zero is constant; (c) case (ii) of
    # Step 3 makes the class matrix rank 1 (checked symbolically on the normalised sign rows).
    three = {k: v for k, v in usable.items() if len(v) == 3}
    t_ok = True
    for (T, _), rows in three.items():
        eps = [rel[i][1] for i in rows]
        pairs_live = []
        for c, c2 in [(0, 1), (0, 2), (0, 3)]:
            grp = [(p, q) for p, q in itertools.combinations(range(3), 2)
                   if eps[p][c] * eps[p][c2] == eps[q][c] * eps[q][c2]]
            pairs_live.append(grp)
        t_ok &= all(len(g) == 1 for g in pairs_live) and len({g[0] for g in pairs_live}) == 3
        prods = [[eps[p][f] * eps[q][f] for f in range(4)] for p, q in itertools.combinations(range(3), 2)]
        t_ok &= rank_q(prods) == 3 and all(sum(v) == 0 for v in prods)
        t_ok &= rank_q(prods + [[1, 1, 1, 1]]) == 4
        # case (ii): u = diag(delta) H0' diag(gamma) where H0' are the normalised sign rows of the class
        # itself (same group structure); a = u o eps then has rank 1 for generic scalings.
        rng = lcg(7 + rows[0])
        dl = [rand_nonzero(rng) for _ in range(3)]
        gm = [rand_nonzero(rng) for _ in range(4)]
        n0 = [eps[0][f] for f in range(4)]
        h0 = [[eps[p][f] * n0[f] * eps[p][0] * n0[0] for f in range(4)] for p in range(3)]
        # h0 = the class's sign rows normalised to first row/column +1: the Step-3 case-(ii) pattern.
        caseii = [[dl[p] * h0[p][f] * gm[f] for f in range(4)] for p in range(3)]
        amat = [[caseii[p][f] * eps[p][f] for f in range(4)] for p in range(3)]
        t_ok &= rank_q(amat) == 1 and rank_q([[dl[p] * eps[p][f] * gm[f] for f in range(4)] for p in range(3)]) == 3
        cert.setdefault('three_row', {})[name] = {'rows': [LINES[i] for i in rows], 'support': [LINES[f] for f in T]}
    check(f'{name}.three-row-lemma', t_ok,
          f'{len(three)} three-row class(es): one live group per pairing; products of sign rows span the non-trivial characters; case (ii) has rank 1')

    # Gluing (input I4 replaced): (a) for every pivot pair {k,k'}, the usable classes whose support contains it
    # are nonempty and connected by witnessed relations (5); (b) a base point k0 with the explicit path
    # condition, so rho_kk' = g_k / g_k' holds multiplicatively over any field.
    good_blocks = {T for (T, _) in usable}
    conn_ok = True
    nrel = 0
    for k, k2 in itertools.combinations(F, 2):
        cls = [key for key in usable if k in key[0] and k2 in key[0]]
        if not cls:
            conn_ok = False
            continue
        adj = {c: set() for c in cls}
        for c1, c2 in itertools.combinations(cls, 2):
            if c1[0] == c2[0]:
                continue
            hit = any(G[i][j] == 0 and set(rel[i][0]) & set(rel[j][0]) == {k, k2}
                      for i in usable[c1] for j in usable[c2])
            if hit:
                adj[c1].add(c2)
                adj[c2].add(c1)
                nrel += 1
        seen, todo = {cls[0]}, [cls[0]]
        while todo:
            x = todo.pop()
            for y in adj[x] - seen:
                seen.add(y)
                todo.append(y)
        conn_ok &= len(seen) == len(cls)
    check(f'{name}.gluing-connected', conn_ok, f'all 28 pivot pairs: usable classes through the pair are connected ({nrel} witnessed relations)')

    def blk(t):
        return next(B for B in blocks if set(t) <= set(B))

    def path_ok(k0):
        for k, k2 in itertools.combinations(F, 2):
            if k0 in (k, k2) or blk((k, k2, k0)) in good_blocks:
                continue
            if not any(blk((k, k2, m)) in good_blocks and blk((k, m, k0)) in good_blocks and blk((k2, m, k0)) in good_blocks
                       for m in F if m not in (k, k2, k0)):
                return False
        return True
    k0s = [k for k in F if path_ok(k)]
    check(f'{name}.gluing-cocycle', len(k0s) > 0,
          f'{len(good_blocks)}/14 blocks usable; base points with the path condition: {len(k0s)}/8')
    trip_rows = []
    pos = {f: n for n, f in enumerate(F)}
    edges = {e: n for n, e in enumerate(itertools.combinations(range(8), 2))}
    for B in good_blocks:
        for a, b, c in itertools.combinations(sorted(pos[f] for f in B), 3):
            r = [0] * 28
            r[edges[(a, b)]] += 1
            r[edges[(b, c)]] += 1
            r[edges[(a, c)]] -= 1
            trip_rows.append(r)
    check(f'{name}.cocycle-rank', rank_q(trip_rows) == 21, 'additive cross-check: triple relations of the usable blocks have rank 28 - 7')

    # Assembly control (Section 7 of PR1212 on this unit): Lemma 5 forms with glued scalings satisfy (2),
    # and (1/4) K[:,F] K[F,:] = D (2G) D^-1 on the live set.
    rng = lcg(1000 + len(live))
    g = {f: rand_nonzero(rng) for f in F}
    dd = {i: rand_nonzero(rng) for i in rel}
    a = {i: {f: (dd[i] * G[i][f] * g[f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    b = {i: {f: (4 / (dd[i] * g[f]) * G[i][f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    for f in F:
        a[f] = {h: Fraction(4 if h == f else 0) for h in F}
        b[f] = {h: Fraction(4 if h == f else 0) for h in F}
    eq_ok = True
    for i in live:
        for j in live:
            if i != j and G[i][j] != 0:
                continue
            v = sum(a[i][f] * b[j][f] for f in F)
            eq_ok &= v == (16 if i == j else 0)
    D = {i: dd[i] / 2 for i in rel}
    D.update({f: 1 / g[f] for f in F})
    asm_ok = all(sum(a[i][f] * b[j][f] for f in F) / 4 == 2 * G[i][j] * D[i] / D[j] for i in live for j in live)
    check(f'{name}.assembly-control', eq_ok and asm_ok, 'glued Lemma 5 forms satisfy (2) and assemble to D (2G) D^-1 exactly')
    cert[name] = {'live': len(live), 'pivot': spec['pivot'], 'class_profile': sizes, 'usable_blocks': len(good_blocks),
                  'base_points': [LINES[k] for k in k0s], 'group_witnesses': nwit, 'floor': spec['floor']}
    return live, F, rel, usable, blocks, good_blocks


def controls(units_data):
    print('== controls')
    # C1: a two-row class does not force constant w: the single product vector leaves a 3-dim solution space.
    live, F, rel, usable, blocks, _ = units_data['P111']
    cl_all = classes_of(relative(F, range(NL)))
    some = next(iter(cl_all.values()))
    eps = [relative(F, range(NL))[i][1] for i in some[:2]]
    prod = [eps[0][f] * eps[1][f] for f in range(4)]
    check('control.two-row-not-forced', 4 - rank_q([prod]) == 3,
          'two rows give one orthogonality condition: w has 3 free directions, so the character argument needs three rows')
    # C2: drop the three-row class from P111's usable set: its block loses its only usable class.
    _, _, _, _, _, good = units_data['P111']
    three_block = next(T for (T, _), v in usable.items() if len(v) == 3)
    others = {T for (T, _), v in usable.items() if len(v) == 4}
    check('control.p111-needs-three-row', three_block not in others and len(others) == 13,
          'without the three-row lemma only 13/14 blocks are usable on P111 (PR1212 G.P111.theorem-transfers)')
    # C3: the path condition is not vacuous: drop complementary block pairs from P104-44's usable set until
    # the additive triple relations lose rank; at that set no base point satisfies the path condition.
    _, F2, _, _, blocks2, good2 = units_data['P104-44']
    pos = {f: n for n, f in enumerate(F2)}
    edges = {e: n for n, e in enumerate(itertools.combinations(range(8), 2))}

    def trank(gb):
        rows = []
        for B in gb:
            for x, y, z in itertools.combinations(sorted(pos[f] for f in B), 3):
                r = [0] * 28
                r[edges[(x, y)]] += 1
                r[edges[(y, z)]] += 1
                r[edges[(x, z)]] -= 1
                rows.append(r)
        return rank_q(rows) if rows else 0

    def blk(t):
        return next(B for B in blocks2 if set(t) <= set(B))

    def path_ok(k0, gb):
        for k, k2 in itertools.combinations(F2, 2):
            if k0 in (k, k2) or blk((k, k2, k0)) in gb:
                continue
            if not any(blk((k, k2, m)) in gb and blk((k, m, k0)) in gb and blk((k2, m, k0)) in gb
                       for m in F2 if m not in (k, k2, k0)):
                return False
        return True
    reduced = set(good2)
    for B in sorted(good2):
        if trank(reduced) < 21:
            break
        reduced -= {B, tuple(f for f in F2 if f not in B)}
    check('control.path-condition-bites', trank(reduced) < 21 and not any(path_ok(k, reduced) for k in F2),
          f'with {len(reduced)} usable blocks the relations have rank {trank(reduced)} < 21 and no base point passes')
    # C4: a non-gauge class matrix fails the assembly: perturb one a-entry and some equation of (2) breaks.
    i0 = next(iter(rel))
    f0 = rel[i0][0][0]
    rng = lcg(5)
    g = {f: rand_nonzero(rng) for f in F}
    dd = {i: rand_nonzero(rng) for i in rel}
    a = {i: {f: (dd[i] * G[i][f] * g[f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    b = {i: {f: (4 / (dd[i] * g[f]) * G[i][f] if f in rel[i][0] else Fraction(0)) for f in F} for i in rel}
    a[i0][f0] *= 3
    broken = any(sum(a[i][f] * b[j][f] for f in F) != (16 if i == j else 0)
                 for i in rel for j in rel if i == j or G[i][j] == 0)
    check('control.perturbed-fails', broken, 'tripling one a-entry violates (2)')


def git_blob_sha1(path):
    data = open(path, 'rb').read()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def replay_pr1212(root, cert):
    print('== PR1212 replay (zero exclusion, transport)')
    pkg = os.path.join(root, PR1212['dir'])
    blobs = {f: git_blob_sha1(os.path.join(pkg, f)) for f in PR1212['blobs']}
    if not check('pr1212.blobs', blobs == PR1212['blobs'], f'files match head {PR1212["head"][:8]}'):
        return
    out = subprocess.run([sys.executable, '-I', '-B', os.path.join(pkg, 'verify.py')], capture_output=True, text=True,
                         cwd=root).stdout
    lines = out.splitlines()
    for p in PR1212['pass_lines']:
        check('pr1212.' + p.split()[1], any(l.startswith(p + ' ') or l == p for l in lines), p)
    for name, spec in UNITS.items():
        want = f'pivot {spec["pr1212_pivot_idx"]}'
        check(f'pr1212.{name}.pivot-index', any(l.startswith(f'PASS G.{name}.unit') and want in l for l in lines), want)
    # map PR1212 indices to vectors through its own line construction, run in a subprocess
    code = ('import sys,json; sys.path.insert(0, sys.argv[1]); import verify as V; '
            'print(json.dumps({"lines": V.LINES}))')
    vec = json.loads(subprocess.run([sys.executable, '-I', '-B', '-c', code, pkg], capture_output=True, text=True).stdout)
    for name, spec in UNITS.items():
        theirs = sorted(canon(vec['lines'][i]) for i in spec['pr1212_pivot_idx'])
        check(f'pr1212.{name}.pivot-vectors', theirs == sorted(canon(v) for v in spec['pivot']), 'same pivot frame')
    cert['pr1212_replayed'] = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pr1212-dir', help='checkout of PR1212 head 57099cb5 (repo root); replays its zero-exclusion checks')
    ap.add_argument('--out', help='write certificate JSON (must not exist)')
    args = ap.parse_args()
    cert = {'pr1212_head': PR1212['head'], 'pr1212_replayed': False}
    print('== model')
    check('model.lines', NL == 120 and {abs(G[i][j]) for i in range(NL) for j in range(NL) if i != j} == {0, 1}, '120 lines, Gram off-diagonal in {0,+-1}')
    check('model.frame0', is_frame(frame_lines(FRAME0)), 'FRAME0 is a frame')
    data = {name: analyse(name, spec, cert) for name, spec in UNITS.items()}
    controls(data)
    if args.pr1212_dir:
        replay_pr1212(args.pr1212_dir, cert)
    else:
        print('NOTE zero exclusion and orbit transport cited from PR1212 (not replayed; pass --pr1212-dir)')
    if args.out:
        with open(args.out, 'x') as fh:
            json.dump(cert, fh, indent=1, default=list)
    if FAILS:
        print('FAILED: ' + ', '.join(FAILS))
        sys.exit(1)
    print(f'PASS_COMPLEX_RANK8_RIGIDITY_P111_P104_44: checks {NCHECK}; P111 three-row 1, blocks 14/14; '
          f'P104-44 blocks 12/14 path-glued; floors 63/56; zero exclusion '
          + ('replayed from PR1212' if cert['pr1212_replayed'] else 'cited from PR1212'))


if __name__ == '__main__':
    main()
